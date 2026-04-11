from odoo import models, fields


class StockMove(models.Model):
    """
    Extend stock.move (حرکت کالا)
    فیلدهای سفارشی روی هر خط انتقال
    """
    _inherit = 'stock.move'

    # ── فیلدهای پایه (اینجا اضافه کن) ──────────────────────────────────

    note = fields.Text(string='توضیحات خط')
