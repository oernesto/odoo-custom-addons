from odoo import fields, models


class PetstylePet(models.Model):
    _name = 'petstyle.pet'
    _description = 'Pet'
    _rec_name = 'pet_name'

    pet_name = fields.Char(string="Pet Name", required=True)
    owner_name = fields.Char(string="Owner Name", required=True)
    size = fields.Selection(
        [('small', "Small"), ('medium', "Medium"), ('large', "Large")],
        string="Size", required=True, default='medium')
    race = fields.Char(string="Race")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
