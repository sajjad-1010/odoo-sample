from odoo import http, fields
from odoo.http import request


class SalesFieldController(http.Controller):

    @http.route('/sales_field/visits', type='json', auth='user')
    def get_visits(self, salesperson_id=None, date_from=None, date_to=None):
        return request.env['field.visit'].get_visits_for_map(
            salesperson_id=salesperson_id,
            date_from=date_from,
            date_to=date_to,
        )

    @http.route('/sales_field/customer_balance', type='json', auth='user')
    def get_customer_balance(self, partner_id=None):
        if not partner_id:
            return {'error': 'partner_id required'}

        user = request.env.user
        is_manager = user.has_group('sales_field.group_sales_field_manager')

        if not is_manager:
            visited = request.env['field.visit'].search_count([
                ('salesperson_id', '=', user.id),
                ('partner_id', '=', partner_id),
            ])
            if not visited:
                return {'error': 'You have not visited this customer.'}

        partner = request.env['res.partner'].browse(partner_id)
        if not partner.exists():
            return {'error': 'Partner not found'}

        invoices = request.env['account.move'].search([
            ('partner_id', '=', partner_id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
        ], order='invoice_date_due asc')

        today = fields.Date.today()
        unpaid = []
        for inv in invoices:
            due = inv.invoice_date_due
            days_overdue = (today - due).days if due and due < today else 0
            unpaid.append({
                'name': inv.name,
                'date': str(inv.invoice_date) if inv.invoice_date else '',
                'amount': inv.amount_residual,
                'due_date': str(due) if due else '',
                'days_overdue': days_overdue,
            })

        currency = request.env.company.currency_id
        return {
            'partner_name': partner.name,
            'partner_phone': partner.phone or '',
            'partner_address': partner.contact_address or '',
            'balance': partner.credit,
            'currency': currency.name,
            'unpaid_invoices': unpaid,
        }

    @http.route('/sales_field/debtors_summary', type='json', auth='user')
    def get_debtors_summary(self):
        user = request.env.user
        is_manager = user.has_group('sales_field.group_sales_field_manager')

        if is_manager:
            partners = request.env['res.partner'].search([
                ('customer_rank', '>', 0),
                ('credit', '>', 0),
            ])
        else:
            visited_partner_ids = request.env['field.visit'].search([
                ('salesperson_id', '=', user.id),
                ('partner_id', '!=', False),
            ]).mapped('partner_id.id')
            partners = request.env['res.partner'].search([
                ('id', 'in', visited_partner_ids),
                ('credit', '>', 0),
            ])

        return {
            'count': len(partners),
            'total': sum(partners.mapped('credit')),
        }
