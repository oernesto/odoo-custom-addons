# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import api, models
from odoo.tools import file_open


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _baroclub_apply_favicon(self):
        """Set the Baro Club monogram as favicon of the default website.

        The default website record is `noupdate`, so a data file can't
        overwrite it when the module is upgraded.
        """
        website = self.env.ref('website.default_website', raise_if_not_found=False)
        if website:
            with file_open('baroclub_website/static/src/img/favicon.png', 'rb') as f:
                website.favicon = base64.b64encode(f.read())
