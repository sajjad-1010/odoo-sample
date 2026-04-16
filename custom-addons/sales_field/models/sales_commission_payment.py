from odoo import models, fields


class SalesCommissionPayment(models.Model):
    _name = 'sales.commission.payment'
    _description = 'Commission Payment'
    _order = 'payment_date desc'

    salesperson_id = fields.Many2one('res.users', string='فروشنده', required=True)
    payment_date = fields.Date(string='تاریخ پرداخت', required=True, default=fields.Date.today)
    amount = fields.Float(string='مبلغ پرداخت شده', required=True)
    note = fields.Text(string='یادداشت')
    paid_by = fields.Many2one('res.users', string='پرداخت کننده', default=lambda self: self.env.user)
