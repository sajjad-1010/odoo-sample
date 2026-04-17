from odoo import models, fields, api


class FieldVisit(models.Model):
    _name = 'field.visit'
    _description = 'Field Sales Visit'
    _order = 'timestamp desc'

    salesperson_id = fields.Many2one(
        'res.users', string='Salesperson',
        required=True, default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_name = fields.Char(string='Customer Name (new)')
    partner_phone = fields.Char(string='Phone')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    timestamp = fields.Datetime(string='Time', default=fields.Datetime.now, required=True)
    notes = fields.Text(string='Notes')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    visit_type = fields.Selection([
        ('visit', 'Visit'),
        ('invoice', 'Invoice'),
        ('new_customer', 'New Customer'),
    ], string='Type', default='visit')
    is_new_customer = fields.Boolean(string='New Customer')
    is_invoice_visit = fields.Boolean(string='Has Invoice')

    has_location = fields.Boolean(compute='_compute_has_location', store=True, search='_search_has_location')
    display_customer = fields.Char(compute='_compute_display_customer', string='Customer', store=True)

    @api.depends('latitude', 'longitude')
    def _compute_has_location(self):
        for rec in self:
            rec.has_location = bool(rec.latitude or rec.longitude)

    def _search_has_location(self, operator, value):
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('latitude', '!=', 0)]
        return [('latitude', '=', 0)]

    @api.depends('partner_id', 'partner_name')
    def _compute_display_customer(self):
        for rec in self:
            rec.display_customer = rec.partner_id.name or rec.partner_name or ''

    def action_open_contact(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_invoice(self):
        self.ensure_one()
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id if self.partner_id else False,
            'invoice_date': self.timestamp.date() if self.timestamp else fields.Date.today(),
            'narration': self.notes or '',
        })
        self.invoice_id = invoice.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_customer_balance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'sales_field.CustomerBalanceDialog',
            'target': 'new',
            'context': {'partner_id': self.partner_id.id},
        }

    @api.model
    def get_visits_for_map(self, salesperson_id=None, date_from=None, date_to=None):
        domain = ['|', ('latitude', '!=', 0), ('longitude', '!=', 0)]
        if salesperson_id:
            domain.append(('salesperson_id', '=', salesperson_id))
        if date_from:
            domain.append(('timestamp', '>=', date_from))
        if date_to:
            domain.append(('timestamp', '<=', date_to))
        visits = self.search(domain)
        return [{
            'id': v.id,
            'salesperson': v.salesperson_id.name,
            'customer': v.display_customer,
            'is_new_customer': v.is_new_customer,
            'is_invoice_visit': v.is_invoice_visit,
            'timestamp': v.timestamp.strftime('%Y-%m-%d %H:%M') if v.timestamp else '',
            'latitude': v.latitude,
            'longitude': v.longitude,
            'notes': v.notes or '',
        } for v in visits]
