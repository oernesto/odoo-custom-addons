# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class BarbershopChair(models.Model):
    _name = 'barbershop.chair'
    _description = 'Barber Chair'
    _order = 'shop_id, sequence, name'

    name = fields.Char(string='Chair', required=True, default='Chair')
    sequence = fields.Integer(default=10)
    shop_id = fields.Many2one(
        'barbershop.shop', string='Barbershop', required=True, ondelete='cascade')
    barber_id = fields.Many2one(
        'barbershop.barber', string='Barber',
        domain="[('shop_ids', '=', shop_id)]",
        help='Barber currently assigned to this chair.')
    active = fields.Boolean(default=True)

    order_ids = fields.One2many('barbershop.order', 'chair_id', string='Orders')
    current_order_id = fields.Many2one(
        'barbershop.order', compute='_compute_current_order_id', string='Current Order', store=True)
    is_busy = fields.Boolean(compute='_compute_current_order_id', string='Busy', store=True)

    _name_shop_uniq = models.Constraint(
        'unique (shop_id, name)',
        'A chair with this name already exists in this barbershop.',
    )

    @api.depends('shop_id.name', 'name')
    def _compute_display_name(self):
        for chair in self:
            chair.display_name = f"{chair.shop_id.name}, {chair.name}"

    @api.depends('order_ids.state')
    def _compute_current_order_id(self):
        for chair in self:
            current_order = chair.order_ids.filtered(lambda o: o.state == 'draft')[:1]
            chair.current_order_id = current_order
            chair.is_busy = bool(current_order)

    def action_open_kanban_order(self):
        """Open the chair's current draft order, or start a new one on this chair."""
        self.ensure_one()
        if self.current_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'barbershop.order',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_id': self.current_order_id.id,
                'target': 'current',
            }
        return self.action_create_order()

    def action_create_order(self):
        """Always start a brand new order on this chair, even if it is currently busy."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('New Order'),
            'res_model': 'barbershop.order',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
            'context': {
                'default_shop_id': self.shop_id.id,
                'default_chair_id': self.id,
                'default_barber_id': self.barber_id.id,
            },
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_except_chair_with_orders(self):
        for chair in self:
            if self.env['barbershop.order'].search_count([('chair_id', '=', chair.id), ('state', '=', 'draft')]):
                raise UserError(self.env._(
                    "You cannot delete a chair that is used by a draft order. Cancel or pay the order(s) first."
                ))
