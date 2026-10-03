# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, api

SHOP_SHARES = {
    'service_haircut_wash_style': 300.0,
    'service_haircut_wash_shave_style': 300.0,
    'service_haircut_wash_beard_eyebrows': 300.0,
    'service_haircut_eyebrows': 300.0,
    'service_beard': 100.0,
    'service_eyebrows': 0.0,
}


def migrate(cr, version):
    """Set the barbershop share on the services shipped in the (noupdate) data."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, amount in SHOP_SHARES.items():
        service = env.ref('barbershop.%s' % xmlid, raise_if_not_found=False)
        if service:
            service.shop_amount = amount
