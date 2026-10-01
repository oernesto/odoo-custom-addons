# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Barbershop',
    'version': '1.0',
    'category': 'Services',
    'sequence': 100,
    'summary': 'Manage barbershops, chairs, barbers, services and orders',
    'description': """
Barbershop Management
======================

This module allows you to manage one or several barbershop locations:

- Barbershops: physical locations with an address.
- Chairs: each barbershop has one or more barber chairs, each one can be
  assigned to a barber.
- Barbers: the people working at the chairs, who can be assigned to one or
  several barbershops.
- Services: the haircut/shave/... services offered, with a price and an
  estimated duration.
- Orders: a ticket for a customer, associating a barbershop, a chair, a
  barber and a customer, with order lines that can be either services or
  regular products sold by the barbershop (combs, waxes, ...).
- Payment methods: simple configuration of the accepted payment types
  (cash, bank transfer or card) per barbershop.

This module is fully independent: it does not depend on Point of Sale or
Accounting, the payment method on an order is only informative.
""",
    'depends': ['mail', 'product', 'stock'],
    'data': [
        'security/barbershop_security.xml',
        'security/ir.model.access.csv',
        'data/barbershop_sequence_data.xml',
        'data/barbershop_payment_method_data.xml',
        'data/barbershop_service_product_data.xml',
        'views/barbershop_shop_views.xml',
        'views/barbershop_chair_views.xml',
        'views/barbershop_barber_views.xml',
        'views/barbershop_service_views.xml',
        'views/barbershop_payment_method_views.xml',
        'views/barbershop_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/barbershop_menus.xml',
        'views/webclient_templates.xml',
    ],
    'demo': [
        'data/barbershop_demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'barbershop/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'author': 'Odoo S.A.',
}
