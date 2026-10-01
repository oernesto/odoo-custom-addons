# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    barbershop_enabled = fields.Boolean(
        related='company_id.barbershop_enabled', string='Barbershop Management', readonly=False)
