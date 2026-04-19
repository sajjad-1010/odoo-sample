from odoo import models, fields, api


class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target'
    _order = 'year desc, month desc'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)
    year = fields.Integer(string='Year', required=True)
    month = fields.Integer(string='Month', required=True)
    target_amount = fields.Float(string='Target Amount', required=True)

    unique_salesperson_period = models.Constraint(
        'UNIQUE(salesperson_id, year, month)',
        'A target for this salesperson and period already exists.',
    )

    MONTHS = ['', 'January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    @api.depends('salesperson_id', 'year', 'month')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.salesperson_id.name} — {self.MONTHS[rec.month]} {rec.year}"
