from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    petstyle_whatsapp_enabled = fields.Boolean(
        string="WhatsApp Reminders",
        config_parameter='petstyle.whatsapp_enabled')
    petstyle_whatsapp_token = fields.Char(
        string="Access Token",
        config_parameter='petstyle.whatsapp_token',
        groups='petstyle.group_petstyle_manager')
    petstyle_whatsapp_phone_id = fields.Char(
        string="Phone Number ID",
        config_parameter='petstyle.whatsapp_phone_id')
    petstyle_whatsapp_template = fields.Char(
        string="Template Name",
        config_parameter='petstyle.whatsapp_template',
        default='bath_order_reminder')
    petstyle_whatsapp_language = fields.Char(
        string="Template Language",
        config_parameter='petstyle.whatsapp_language',
        default='es')
    petstyle_whatsapp_lead_minutes = fields.Integer(
        string="Send Reminder Before (minutes)",
        config_parameter='petstyle.whatsapp_lead_minutes',
        default=60)
    petstyle_whatsapp_country_code = fields.Char(
        string="Default Country Code",
        config_parameter='petstyle.whatsapp_country_code',
        help="Prepended to phone numbers that do not start with '+', e.g. 593.")
