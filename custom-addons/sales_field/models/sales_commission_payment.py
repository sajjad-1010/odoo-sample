from odoo import models, fields


class SalesCommissionPayment(models.Model):
    _name = 'sales.commission.payment'
    _description = 'Commission Payment'
    _order = 'payment_date desc'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    amount = fields.Float(string='Amount', required=True)
    note = fields.Text(string='Notes')
    paid_by = fields.Many2one('res.users', string='Paid By', default=lambda self: self.env.user)
