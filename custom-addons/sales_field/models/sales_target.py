from odoo import models, fields


class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target'
    _order = 'year desc, month desc'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)
    year = fields.Integer(string='Year', required=True)
    month = fields.Integer(string='Month', required=True)
    target_amount = fields.Float(string='Target Amount', required=True)

    _sql_constraints = [
        ('unique_salesperson_period', 'UNIQUE(salesperson_id, year, month)',
         'A target for this salesperson and period already exists.'),
    ]

    def name_get(self):
        result = []
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        for rec in self:
            name = f"{rec.salesperson_id.name} — {months[rec.month]} {rec.year}"
            result.append((rec.id, name))
        return result
