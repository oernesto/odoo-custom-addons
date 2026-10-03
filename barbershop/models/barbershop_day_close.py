# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time, timedelta

import pytz

from odoo import Command, api, fields, models


class BarbershopDayClose(models.TransientModel):
    _name = 'barbershop.day.close'
    _description = 'Barbershop Day Closing'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    shop_id = fields.Many2one(
        'barbershop.shop', string='Barbershop',
        default=lambda self: self.env['barbershop.shop'].search(
            [('company_id', '=', self.env.company.id)], limit=1))
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    line_ids = fields.One2many(
        'barbershop.day.close.line', 'close_id', string='Breakdown',
        compute='_compute_line_ids')
    barber_total = fields.Monetary(string='Barbers Share', compute='_compute_totals')
    shop_total = fields.Monetary(string='Barbershop Share', compute='_compute_totals')
    tip_total = fields.Monetary(string='Tips', compute='_compute_totals')
    order_count = fields.Integer(string='Orders', compute='_compute_totals')

    def _get_day_orders(self):
        self.ensure_one()
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        start = tz.localize(datetime.combine(self.date, time.min))
        stop = start + timedelta(days=1)
        to_utc = lambda dt: dt.astimezone(pytz.utc).replace(tzinfo=None)
        domain = [
            ('state', '=', 'paid'),
            ('date_order', '>=', to_utc(start)),
            ('date_order', '<', to_utc(stop)),
            ('company_id', '=', self.company_id.id),
        ]
        if self.shop_id:
            domain.append(('shop_id', '=', self.shop_id.id))
        return self.env['barbershop.order'].search(domain)

    @api.depends('date', 'shop_id', 'company_id')
    def _compute_line_ids(self):
        for close in self:
            by_barber = {}
            orders = close._get_day_orders() if close.date else self.env['barbershop.order']
            for order in orders:
                entry = by_barber.setdefault(order.barber_id.id, {
                    'barber_id': order.barber_id.id, 'barber_amount': 0.0,
                    'shop_amount': 0.0, 'tip_amount': 0.0, 'order_count': 0})
                shop, barber = order._get_day_close_split()
                entry['shop_amount'] += shop
                entry['barber_amount'] += barber
                entry['tip_amount'] += order.tip_amount
                entry['order_count'] += 1
            rows = sorted(by_barber.values(), key=lambda r: r['barber_id'])
            close.line_ids = [Command.clear()] + [Command.create(r) for r in rows]

    @api.depends('line_ids')
    def _compute_totals(self):
        for close in self:
            close.barber_total = sum(close.line_ids.mapped('barber_amount'))
            close.shop_total = sum(close.line_ids.mapped('shop_amount'))
            close.tip_total = sum(close.line_ids.mapped('tip_amount'))
            close.order_count = sum(close.line_ids.mapped('order_count'))


class BarbershopDayCloseLine(models.TransientModel):
    _name = 'barbershop.day.close.line'
    _description = 'Barbershop Day Closing Line'

    close_id = fields.Many2one('barbershop.day.close', ondelete='cascade')
    currency_id = fields.Many2one(related='close_id.currency_id')
    barber_id = fields.Many2one('barbershop.barber', string='Barber')
    order_count = fields.Integer(string='Orders')
    barber_amount = fields.Monetary(string='Barber Share')
    shop_amount = fields.Monetary(string='Barbershop Share')
    tip_amount = fields.Monetary(string='Tip')
