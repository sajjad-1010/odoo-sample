from odoo import models, fields, api
from datetime import date


class ResUsersCommission(models.Model):
    _inherit = 'res.users'

    current_month_sales = fields.Float(
        string='فروش این ماه', compute='_compute_commission_stats', digits=(16, 2))
    current_month_commission = fields.Float(
        string='کمیسیون این ماه', compute='_compute_commission_stats', digits=(16, 2))
    current_month_target = fields.Float(
        string='هدف این ماه', compute='_compute_commission_stats', digits=(16, 2))
    target_progress = fields.Float(
        string='پیشرفت هدف (%)', compute='_compute_commission_stats', digits=(5, 1))
    total_commission_earned = fields.Float(
        string='کل کمیسیون', compute='_compute_commission_stats', digits=(16, 2))
    total_commission_paid = fields.Float(
        string='کل پرداخت شده', compute='_compute_commission_stats', digits=(16, 2))
    commission_balance = fields.Float(
        string='مانده کمیسیون', compute='_compute_commission_stats', digits=(16, 2))

    def _compute_commission_stats(self):
        today = date.today()
        year = today.year
        month = today.month
        month_start = f"{year}-{month:02d}-01"
        if month == 12:
            month_end = f"{year + 1}-01-01"
        else:
            month_end = f"{year}-{month + 1:02d}-01"

        for user in self:
            # فروش این ماه از فاکتورهای تایید شده
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_user_id', '=', user.id),
                ('invoice_date', '>=', month_start),
                ('invoice_date', '<', month_end),
            ])
            month_sales = sum(invoices.mapped('amount_untaxed'))

            # کمیسیون این ماه
            config = self.env['sales.commission.config'].search([
                ('salesperson_id', '=', user.id),
                ('is_active', '=', True),
            ], limit=1)
            month_commission = config.compute_commission(month_sales) if config else 0.0

            # کل کمیسیون (همه فاکتورهای تاریخ)
            all_invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_user_id', '=', user.id),
            ])
            total_sales = sum(all_invoices.mapped('amount_untaxed'))
            total_earned = config.compute_commission(total_sales) if config else 0.0

            # کل پرداخت شده
            total_paid = sum(self.env['sales.commission.payment'].search([
                ('salesperson_id', '=', user.id),
            ]).mapped('amount'))

            # هدف این ماه
            target_rec = self.env['sales.target'].search([
                ('salesperson_id', '=', user.id),
                ('year', '=', year),
                ('month', '=', month),
            ], limit=1)
            month_target = target_rec.target_amount if target_rec else 0.0
            progress = (month_sales / month_target * 100) if month_target else 0.0

            user.current_month_sales = month_sales
            user.current_month_commission = month_commission
            user.current_month_target = month_target
            user.target_progress = progress
            user.total_commission_earned = total_earned
            user.total_commission_paid = total_paid
            user.commission_balance = total_earned - total_paid
