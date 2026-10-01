# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class BarbershopShop(models.Model):
    _name = 'barbershop.shop'
    _description = 'Barbershop'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    active = fields.Boolean(default=True)

    chair_ids = fields.One2many('barbershop.chair', 'shop_id', string='Chairs')
    chair_count = fields.Integer(compute='_compute_chair_count', string='Chair Count')
    payment_method_ids = fields.Many2many(
        'barbershop.payment.method', string='Accepted Payment Methods',
        help='Payment methods that customers can use to pay orders in this barbershop.')
    order_ids = fields.One2many('barbershop.order', 'shop_id', string='Orders')
    order_count = fields.Integer(compute='_compute_order_count', string='Order Count')

    @api.depends('chair_ids')
    def _compute_chair_count(self):
        for shop in self:
            shop.chair_count = len(shop.chair_ids)

    def _compute_order_count(self):
        order_data = self.env['barbershop.order']._read_group(
            [('shop_id', 'in', self.ids)], ['shop_id'], ['__count'])
        order_count_by_shop = {shop.id: count for shop, count in order_data}
        for shop in self:
            shop.order_count = order_count_by_shop.get(shop.id, 0)

    def action_view_chairs(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('barbershop.action_barbershop_chair')
        action['domain'] = [('shop_id', '=', self.id)]
        action['context'] = {'default_shop_id': self.id}
        return action

    def action_view_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('barbershop.action_barbershop_order')
        action['domain'] = [('shop_id', '=', self.id)]
        action['context'] = {'default_shop_id': self.id}
        return action

    @api.ondelete(at_uninstall=False)
    def _unlink_except_shop_with_orders(self):
        for shop in self:
            if self.env['barbershop.order'].search_count([('shop_id', '=', shop.id)]):
                raise UserError(self.env._(
                    "You cannot delete a barbershop that already has orders. "
                    "Archive it instead."
                ))
