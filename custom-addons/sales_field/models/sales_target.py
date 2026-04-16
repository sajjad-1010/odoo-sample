from odoo import models, fields


class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target'
    _order = 'year desc, month desc'

    salesperson_id = fields.Many2one('res.users', string='فروشنده', required=True)
    year = fields.Integer(string='سال', required=True)
    month = fields.Integer(string='ماه', required=True)
    target_amount = fields.Float(string='هدف فروش', required=True)

    _sql_constraints = [
        ('unique_salesperson_period', 'UNIQUE(salesperson_id, year, month)',
         'برای این فروشنده در این دوره قبلاً هدف تعریف شده است.'),
    ]

    def name_get(self):
        result = []
        months = ['', 'ژانویه', 'فوریه', 'مارس', 'آوریل', 'می', 'ژوئن',
                  'ژوئیه', 'اوت', 'سپتامبر', 'اکتبر', 'نوامبر', 'دسامبر']
        for rec in self:
            name = f"{rec.salesperson_id.name} — {months[rec.month]} {rec.year}"
            result.append((rec.id, name))
        return result
