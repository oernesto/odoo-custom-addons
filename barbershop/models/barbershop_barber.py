# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BarbershopBarber(models.Model):
    _name = 'barbershop.barber'
    _description = 'Barber'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    image_1920 = fields.Image(string='Image')
    user_id = fields.Many2one(
        'res.users', string='Related User',
        help='Odoo user linked to this barber, used to default the barber on new orders.')
    shop_ids = fields.Many2many(
        'barbershop.shop', string='Barbershops',
        help='Barbershops where this barber works.')
    chair_ids = fields.One2many(
        'barbershop.chair', 'barber_id', string='Assigned Chairs')
    active = fields.Boolean(default=True)
