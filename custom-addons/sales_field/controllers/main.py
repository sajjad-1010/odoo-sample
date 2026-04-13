from odoo import http
from odoo.http import request


class SalesFieldController(http.Controller):

    @http.route('/sales_field/visits', type='json', auth='user')
    def get_visits(self, salesperson_id=None, date_from=None, date_to=None):
        return request.env['field.visit'].get_visits_for_map(
            salesperson_id=salesperson_id,
            date_from=date_from,
            date_to=date_to,
        )
