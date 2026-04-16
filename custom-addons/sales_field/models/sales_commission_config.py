from odoo import models, fields, api


class SalesCommissionConfig(models.Model):
    _name = 'sales.commission.config'
    _description = 'Commission Configuration'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)
    commission_type = fields.Selection([
        ('fixed', 'درصد ثابت'),
        ('tiered', 'پلکانی'),
    ], string='نوع کمیسیون', required=True, default='fixed')
    calc_method = fields.Selection([
        ('monthly', 'ماهانه'),
        ('per_invoice', 'هر فاکتور'),
    ], string='روش محاسبه', required=True, default='monthly')
    fixed_rate = fields.Float(string='درصد ثابت', digits=(5, 2))
    is_active = fields.Boolean(string='فعال', default=True)
    note = fields.Text(string='یادداشت')
    tier_ids = fields.One2many('sales.commission.tier', 'config_id', string='جدول پلکانی')

    _sql_constraints = [
        ('unique_salesperson', 'UNIQUE(salesperson_id)', 'هر فروشنده فقط یک تنظیم کمیسیون میتواند داشته باشد.'),
    ]

    def compute_commission(self, amount):
        self.ensure_one()
        if self.commission_type == 'fixed':
            return amount * self.fixed_rate / 100
        elif self.commission_type == 'tiered':
            for tier in self.tier_ids.sorted('min_amount'):
                if amount >= tier.min_amount and (tier.max_amount == 0 or amount < tier.max_amount):
                    return amount * tier.rate / 100
        return 0.0


class SalesCommissionTier(models.Model):
    _name = 'sales.commission.tier'
    _description = 'Commission Tier'
    _order = 'min_amount asc'

    config_id = fields.Many2one('sales.commission.config', string='تنظیم', required=True, ondelete='cascade')
    min_amount = fields.Float(string='از مقدار', required=True)
    max_amount = fields.Float(string='تا مقدار (0=بی‌نهایت)', default=0)
    rate = fields.Float(string='درصد', required=True, digits=(5, 2))
