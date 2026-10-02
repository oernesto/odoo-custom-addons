from datetime import datetime, time as dt_time, timedelta

import pytz

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PetstyleBathOrder(models.Model):
    _name = 'petstyle.bath.order'
    _description = 'Bath Order'
    _order = 'date, time'

    pet_id = fields.Many2one('petstyle.pet', string="Pet", required=True)
    pet_name = fields.Char(related='pet_id.pet_name', string="Pet Name")
    owner_name = fields.Char(related='pet_id.owner_name', string="Owner Name")
    size = fields.Selection(related='pet_id.size', string="Size")
    race = fields.Char(related='pet_id.race', string="Race")
    phone = fields.Char(related='pet_id.phone', string="Phone")
    email = fields.Char(related='pet_id.email', string="Email")
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    time = fields.Float(string="Time", required=True, help="Time of day, e.g. 14.5 = 14:30")
    payment_method = fields.Selection(
        [('cash', "Cash"), ('card', "Card"), ('transfer', "Bank Transfer")],
        string="Payment Method", default='cash')
    price = fields.Float(string="Price")
    state = fields.Selection(
        [('pending', "Pending"), ('paid', "Paid")],
        string="State", default='pending', required=True)

    start_datetime = fields.Datetime(
        string="Start", compute='_compute_datetimes', store=True)
    stop_datetime = fields.Datetime(
        string="End", compute='_compute_datetimes', store=True)

    @api.depends('date', 'time')
    def _compute_datetimes(self):
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        for order in self:
            if not order.date:
                order.start_datetime = order.stop_datetime = False
                continue
            naive = datetime.combine(order.date, dt_time.min) + timedelta(hours=order.time)
            start = tz.localize(naive).astimezone(pytz.utc).replace(tzinfo=None)
            order.start_datetime = start
            order.stop_datetime = start + timedelta(minutes=30)

    def action_pay(self):
        self.state = 'paid'

    def action_pending(self):
        self.state = 'pending'

    @api.constrains('date', 'time')
    def _check_no_overlap(self):
        min_gap = 0.5  # hours
        for order in self:
            if not 0 <= order.time < 24:
                raise ValidationError(self.env._("Invalid time."))
            conflicts = self.search([
                ('id', '!=', order.id),
                ('date', '=', order.date),
                ('time', '>', order.time - min_gap),
                ('time', '<', order.time + min_gap),
            ])
            if conflicts:
                raise ValidationError(self.env._(
                    "Orders must be at least 30 minutes apart. Conflicts with: %(pets)s.",
                    pets=", ".join(conflicts.mapped('pet_name')),
                ))
