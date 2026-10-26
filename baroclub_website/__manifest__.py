# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Baro Club Website',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Landing page for Baro Club Barbería',
    'description': """
Baro Club Website
=================

Home page of Baro Club Barbería (Ciudad Vieja, Montevideo) built with the
Odoo Website app: hero, services, barber, venue gallery, reviews and
contact/opening hours. It replaces the default homepage and is fully
editable from the website editor.
""",
    'depends': ['website'],
    'data': [
        'data/website_data.xml',
        'views/homepage_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'baroclub_website/static/src/scss/baroclub.scss',
        ],
    },
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'application': False,
    'author': 'Baro Club',
    'license': 'LGPL-3',
}
