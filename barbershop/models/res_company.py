# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    barbershop_enabled = fields.Boolean(
        string='Barbershop Management',
        default=True,
        help='Enables the barbershop features (shops, chairs, barbers, services and orders) '
             'for this company.',
    )
