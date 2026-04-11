from odoo import models, fields, api


class StockPicking(models.Model):
    """
    Extend stock.picking (Transfer / Receipt / Delivery)
    فیلدهای سفارشی روی رسید، حواله و انتقال
    """
    _inherit = 'stock.picking'

    # ── فیلدهای پایه (اینجا اضافه کن) ──────────────────────────────────

    note = fields.Text(string='توضیحات')

    # ── Computed ────────────────────────────────────────────────────────

    total_qty = fields.Float(
        string='تعداد کل',
        compute='_compute_total_qty',
        store=True,
    )

    # ── Methods ─────────────────────────────────────────────────────────

    @api.depends('move_ids.product_uom_qty')
    def _compute_total_qty(self):
        for picking in self:
            picking.total_qty = sum(picking.move_ids.mapped('product_uom_qty'))
