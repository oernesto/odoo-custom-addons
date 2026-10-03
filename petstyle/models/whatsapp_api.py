import logging
import re

import requests

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com/v21.0/%s/messages"


class PetstyleWhatsapp(models.AbstractModel):
    _name = 'petstyle.whatsapp'
    _description = 'WhatsApp Cloud API connector'

    def _normalize_phone(self, phone):
        """Return the phone in international format, digits only."""
        phone = (phone or '').strip()
        digits = re.sub(r'\D', '', phone)
        if not digits:
            raise UserError(self.env._("The pet has no phone number."))
        if phone.startswith('+'):
            return digits
        country = re.sub(r'\D', '', self.env['ir.config_parameter'].sudo().get_param(
            'petstyle.whatsapp_country_code') or '')
        return country + digits.lstrip('0')

    def _send_template(self, phone, params):
        """Send the configured template with positional body ``params``."""
        icp = self.env['ir.config_parameter'].sudo()
        token = icp.get_param('petstyle.whatsapp_token')
        phone_id = icp.get_param('petstyle.whatsapp_phone_id')
        template = icp.get_param('petstyle.whatsapp_template')
        if not (token and phone_id and template):
            raise UserError(self.env._("WhatsApp is not configured (Settings > PetStyle)."))
        payload = {
            'messaging_product': 'whatsapp',
            'to': self._normalize_phone(phone),
            'type': 'template',
            'template': {
                'name': template,
                'language': {'code': icp.get_param('petstyle.whatsapp_language') or 'es'},
                'components': [{
                    'type': 'body',
                    'parameters': [{'type': 'text', 'text': p} for p in params],
                }],
            },
        }
        try:
            response = requests.post(
                GRAPH_URL % phone_id,
                json=payload,
                headers={'Authorization': 'Bearer %s' % token},
                timeout=15,
            )
        except requests.RequestException as e:
            raise UserError(self.env._("WhatsApp request failed: %s", e)) from e
        if not response.ok:
            try:
                detail = response.json().get('error', {}).get('message')
            except ValueError:
                detail = None
            _logger.warning("WhatsApp API error %s: %s", response.status_code, response.text)
            raise UserError(self.env._(
                "WhatsApp API error %(code)s: %(detail)s",
                code=response.status_code, detail=detail or response.reason))
        return response.json()
