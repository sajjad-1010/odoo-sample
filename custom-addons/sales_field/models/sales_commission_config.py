from odoo import models, fields, api


class SalesCommissionConfig(models.Model):
    _name = 'sales.commission.config'
    _description = 'Commission Configuration'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)
    commission_type = fields.Selection([
        ('fixed', 'Fixed Rate'),
        ('tiered', 'Tiered'),
    ], string='Commission Type', required=True, default='fixed')
    calc_method = fields.Selection([
        ('monthly', 'Monthly'),
        ('per_invoice', 'Per Invoice'),
    ], string='Calculation Method', required=True, default='monthly')
    fixed_rate = fields.Float(string='Fixed Rate (%)', digits=(5, 2))
    is_active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Notes')
    tier_ids = fields.One2many('sales.commission.tier', 'config_id', string='Tiered Table')

    unique_salesperson = models.Constraint(
        'UNIQUE(salesperson_id)',
        'Each salesperson can only have one commission config.',
    )

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

    config_id = fields.Many2one('sales.commission.config', string='Config', required=True, ondelete='cascade')
    min_amount = fields.Float(string='From Amount', required=True)
    max_amount = fields.Float(string='To Amount (0=Unlimited)', default=0)
    rate = fields.Float(string='Rate (%)', required=True, digits=(5, 2))
