from odoo import models, fields, api
from datetime import date
from collections import defaultdict


class ResUsersCommission(models.Model):
    _inherit = 'res.users'

    current_month_sales = fields.Float(
        string='This Month Sales', compute='_compute_commission_stats', digits=(16, 2))
    current_month_commission = fields.Float(
        string='This Month Commission', compute='_compute_commission_stats', digits=(16, 2))
    current_month_target = fields.Float(
        string='This Month Target', compute='_compute_commission_stats', digits=(16, 2))
    target_progress = fields.Float(
        string='Target Progress (%)', compute='_compute_commission_stats', digits=(5, 1))
    total_commission_earned = fields.Float(
        string='Total Commission Earned', compute='_compute_commission_stats', digits=(16, 2))
    total_commission_paid = fields.Float(
        string='Total Commission Paid', compute='_compute_commission_stats', digits=(16, 2))
    commission_balance = fields.Float(
        string='Commission Balance', compute='_compute_commission_stats', digits=(16, 2))

    def _compute_commission_stats(self):
        today = date.today()
        year, month = today.year, today.month
        month_start = date(year, month, 1)
        month_end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

        user_ids = self.ids

        # single query for all invoices of all users
        all_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_user_id', 'in', user_ids),
        ])
        month_sales_by_user = defaultdict(float)
        monthly_by_user = defaultdict(lambda: defaultdict(float))
        for inv in all_invoices:
            uid = inv.invoice_user_id.id
            if inv.invoice_date:
                key = (inv.invoice_date.year, inv.invoice_date.month)
                monthly_by_user[uid][key] += inv.amount_untaxed
                if month_start <= inv.invoice_date < month_end:
                    month_sales_by_user[uid] += inv.amount_untaxed

        # single query for all commission configs
        configs = self.env['sales.commission.config'].search([
            ('salesperson_id', 'in', user_ids),
            ('is_active', '=', True),
        ])
        config_by_user = {c.salesperson_id.id: c for c in configs}

        # single query for all payments
        payments = self.env['sales.commission.payment'].search([
            ('salesperson_id', 'in', user_ids),
        ])
        paid_by_user = defaultdict(float)
        for p in payments:
            paid_by_user[p.salesperson_id.id] += p.amount

        # single query for all monthly targets
        targets = self.env['sales.target'].search([
            ('salesperson_id', 'in', user_ids),
            ('year', '=', year),
            ('month', '=', month),
        ])
        target_by_user = {t.salesperson_id.id: t.target_amount for t in targets}

        for user in self:
            config = config_by_user.get(user.id)
            month_sales = month_sales_by_user.get(user.id, 0.0)
            month_commission = config.compute_commission(month_sales) if config else 0.0
            total_earned = sum(
                config.compute_commission(amt) for amt in monthly_by_user[user.id].values()
            ) if config else 0.0
            total_paid = paid_by_user.get(user.id, 0.0)
            month_target = target_by_user.get(user.id, 0.0)
            progress = (month_sales / month_target * 100) if month_target else 0.0

            user.current_month_sales = month_sales
            user.current_month_commission = month_commission
            user.current_month_target = month_target
            user.target_progress = progress
            user.total_commission_earned = total_earned
            user.total_commission_paid = total_paid
            user.commission_balance = total_earned - total_paid
