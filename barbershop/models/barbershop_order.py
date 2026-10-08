# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class BarbershopOrder(models.Model):
    _name = 'barbershop.order'
    _description = 'Barbershop Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc, id desc'

    name = fields.Char(
        string='Order Number', required=True, copy=False, readonly=True, default='New')
    shop_id = fields.Many2one(
        'barbershop.shop', string='Barbershop', required=True, tracking=True,
        default=lambda self: self.env['barbershop.shop'].search(
            [('company_id', '=', self.env.company.id)], limit=1))
    chair_id = fields.Many2one(
        'barbershop.chair', string='Chair', tracking=True,
        domain="[('shop_id', '=', shop_id)]")
    barber_id = fields.Many2one(
        'barbershop.barber', string='Barber', required=True, tracking=True,
        domain="[('shop_ids', '=', shop_id)]")
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True)
    date_order = fields.Datetime(
        string='Order Date', required=True, default=fields.Datetime.now)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('paid', 'Paid'),
         ('cancelled', 'Cancelled')],
        string='Status', default='draft', copy=False, tracking=True, required=True)
    payment_method_id = fields.Many2one(
        'barbershop.payment.method', string='Payment Method', tracking=True,
        domain="[('id', 'in', available_payment_method_ids)]")
    available_payment_method_ids = fields.Many2many(
        'barbershop.payment.method', compute='_compute_available_payment_method_ids')
    line_ids = fields.One2many('barbershop.order.line', 'order_id', string='Order Lines', copy=True)
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', store=True)
    tip_amount = fields.Monetary(
        string='Tip', tracking=True,
        help='Tip left by the customer. It is informative only and is not included in the order total nor in any report totals.')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    note = fields.Text(string='Note')

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))

    @api.depends('shop_id')
    def _compute_available_payment_method_ids(self):
        for order in self:
            # A shop without explicit configuration accepts every payment method.
            order.available_payment_method_ids = (
                order.shop_id.payment_method_ids
                or self.env['barbershop.payment.method'].search([]))

    @api.onchange('shop_id')
    def _onchange_shop_id(self):
        for order in self:
            if order.chair_id and order.chair_id.shop_id != order.shop_id:
                order.chair_id = False
            if order.barber_id and order.shop_id not in order.barber_id.shop_ids:
                order.barber_id = False
            if order.payment_method_id and order.payment_method_id not in order.available_payment_method_ids:
                order.payment_method_id = False

    @api.onchange('chair_id')
    def _onchange_chair_id(self):
        for order in self:
            if order.chair_id.barber_id:
                order.barber_id = order.chair_id.barber_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('barbershop.order') or 'New'
        return super().create(vals_list)

    def _get_day_close_split(self):
        """Return (barbershop amount, barber amount) of the order for the day closing.

        Service lines give the barbershop the service's fixed share (capped at the
        line subtotal) and the rest to the barber; product lines go entirely to the
        barbershop. The tip is not part of the split.
        """
        self.ensure_one()
        shop = barber = 0.0
        for line in self.line_ids:
            if line.line_type == 'service':
                line_shop = min(line.service_id.shop_amount * line.quantity, line.price_subtotal)
                shop += line_shop
                barber += line.price_subtotal - line_shop
            else:
                shop += line.price_subtotal
        return shop, barber

    def action_confirm_payment(self):
        for order in self:
            if not order.line_ids:
                raise UserError(self.env._("You cannot confirm an order without any line."))
            if not order.payment_method_id:
                raise UserError(self.env._("Please select a payment method before confirming the payment."))
            order.state = 'paid'
        return True

    def action_cancel(self):
        self.state = 'cancelled'
        return True

    def action_set_draft(self):
        self.state = 'draft'
        return True

    @api.model
    def get_dashboard_data(self, date_from, date_to):
        """Aggregate paid orders between date_from and date_to (UTC datetime strings,
        date_to excluded) for the barbershop statistics dashboard."""
        domain = [
            ('state', '=', 'paid'),
            ('date_order', '>=', date_from),
            ('date_order', '<', date_to),
        ]
        orders = self.search(domain)

        by_chair = {}
        for order in orders:
            chair = order.chair_id
            key = chair.id or 0
            entry = by_chair.setdefault(key, {
                'chair_id': chair.id,
                'chair_name': chair.display_name if chair else self.env._('No Chair'),
                'shop_name': chair.shop_id.name if chair else (order.shop_id.name or ''),
                'order_count': 0,
                'amount_total': 0.0,
                'shop_amount': 0.0,
                'barber_amount': 0.0,
                'tip_amount': 0.0,
                'partner_ids': set(),
            })
            shop_amount, barber_amount = order._get_day_close_split()
            entry['order_count'] += 1
            entry['amount_total'] += order.amount_total
            entry['shop_amount'] += shop_amount
            entry['barber_amount'] += barber_amount
            entry['tip_amount'] += order.tip_amount
            entry['partner_ids'].add(order.partner_id.id)

        by_chair_list = [{
            'chair_id': entry['chair_id'],
            'chair_name': entry['chair_name'],
            'shop_name': entry['shop_name'],
            'order_count': entry['order_count'],
            'customer_count': len(entry['partner_ids']),
            'amount_total': entry['amount_total'],
            'shop_amount': entry['shop_amount'],
            'barber_amount': entry['barber_amount'],
            'tip_amount': entry['tip_amount'],
        } for entry in by_chair.values()]
        by_chair_list.sort(key=lambda r: r['amount_total'], reverse=True)

        timeseries, granularity = self._get_dashboard_timeseries(orders, date_from, date_to)

        return {
            'kpi': {
                'order_count': len(orders),
                'customer_count': len(orders.partner_id),
                'amount_total': sum(orders.mapped('amount_total')),
                'shop_amount': sum(r['shop_amount'] for r in by_chair_list),
                'barber_amount': sum(r['barber_amount'] for r in by_chair_list),
                'tip_amount': sum(orders.mapped('tip_amount')),
            },
            'by_chair': by_chair_list,
            'timeseries': timeseries,
            'granularity': granularity,
            'currency_id': self.env.company.currency_id.id,
        }

    def _get_dashboard_timeseries(self, orders, date_from, date_to):
        """Bucket the given paid orders into weekly or monthly points (in the current
        user's timezone), automatically choosing the granularity from the size of the
        [date_from, date_to) range: a range longer than ~2 months is grouped by month,
        otherwise by week (Monday-aligned)."""
        tz = pytz.timezone(self.env.user.tz or 'UTC')

        def to_local(naive_utc_dt):
            return pytz.utc.localize(naive_utc_dt).astimezone(tz)

        start_local = to_local(fields.Datetime.from_string(date_from))
        end_local = to_local(fields.Datetime.from_string(date_to))
        granularity = 'month' if (end_local - start_local).days > 60 else 'week'

        def bucket_key_and_label(dt_local):
            if granularity == 'month':
                key = (dt_local.year, dt_local.month, 1)
                label = dt_local.strftime('%b %Y')
            else:
                monday = dt_local - timedelta(days=dt_local.weekday())
                key = (monday.year, monday.month, monday.day)
                label = monday.strftime('%d %b')
            return key, label

        buckets = {}

        # Pre-fill every bucket in the range so empty periods show as zero instead
        # of being skipped in the chart.
        cursor = start_local.replace(day=1) if granularity == 'month' else (
            start_local - timedelta(days=start_local.weekday()))
        step = relativedelta(months=1) if granularity == 'month' else timedelta(days=7)
        while cursor < end_local:
            key, label = bucket_key_and_label(cursor)
            buckets[key] = {'label': label, 'order_count': 0, 'amount_total': 0.0}
            cursor += step

        for order in orders:
            key, label = bucket_key_and_label(to_local(order.date_order))
            entry = buckets.setdefault(key, {'label': label, 'order_count': 0, 'amount_total': 0.0})
            entry['order_count'] += 1
            entry['amount_total'] += order.amount_total

        timeseries = [buckets[key] for key in sorted(buckets.keys())]
        return timeseries, granularity
