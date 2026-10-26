# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models


def _post_init_hook(env):
    """Point every existing website's homepage (a per-website copy of the
    generic one) to the Baro Club template."""
    view = env.ref('baroclub_website.home')
    env['website.page'].with_context(active_test=False).search([
        ('url', '=', '/'),
        ('website_id', '!=', False),
    ]).write({
        'view_id': view.id,
        'header_visible': False,
        'footer_visible': False,
    })
