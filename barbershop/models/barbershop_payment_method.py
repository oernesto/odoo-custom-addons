# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BarbershopPaymentMethod(models.Model):
    _name = 'barbershop.payment.method'
    _description = 'Barbershop Payment Method'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    payment_type = fields.Selection(
        [('cash', 'Cash'),
         ('transfer', 'Bank Transfer'),
         ('card', 'Card')],
        string='Type', required=True, default='cash',
        help='Broad category this payment method belongs to.')
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company', string='Company',
        help='Leave empty to make this payment method available to every company.')
    active = fields.Boolean(default=True)
