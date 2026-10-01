# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BarbershopOrderLine(models.Model):
    _name = 'barbershop.order.line'
    _description = 'Barbershop Order Line'
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one(
        'barbershop.order', string='Order', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        [('service', 'Service'), ('product', 'Product')],
        string='Type', required=True, default='service')
    service_id = fields.Many2one('barbershop.service', string='Service')
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True)]")
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    price_subtotal = fields.Monetary(
        string='Subtotal', compute='_compute_price_subtotal', store=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Currency', readonly=True, store=True)
    company_id = fields.Many2one(
        related='order_id.company_id', string='Company', readonly=True, store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange('line_type')
    def _onchange_line_type(self):
        for line in self:
            if line.line_type == 'service':
                line.product_id = False
            else:
                line.service_id = False

    @api.onchange('service_id')
    def _onchange_service_id(self):
        for line in self:
            if line.service_id:
                line.name = line.service_id.name
                line.price_unit = line.service_id.price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name
                line.price_unit = line.product_id.lst_price

    @api.constrains('line_type', 'service_id', 'product_id')
    def _check_line_type_consistency(self):
        for line in self:
            if line.line_type == 'service' and not line.service_id:
                raise ValidationError(self.env._("Please select a service for service lines."))
            if line.line_type == 'product' and not line.product_id:
                raise ValidationError(self.env._("Please select a product for product lines."))
