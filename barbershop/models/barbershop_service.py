# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BarbershopService(models.Model):
    _name = 'barbershop.service'
    _description = 'Barbershop Service'
    _order = 'sequence, name'

    name = fields.Char(string='Service', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    price = fields.Monetary(string='Price', required=True, default=0.0)
    duration = fields.Float(
        string='Duration (minutes)', default=30.0,
        help='Estimated time needed to perform this service.')
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    active = fields.Boolean(default=True)
