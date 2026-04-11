from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    x_pos = fields.Integer(
        string='Map X Position',
        default=0,
        help='Horizontal grid position on the Warehouse Mini-Map (0 = not placed)',
    )
    y_pos = fields.Integer(
        string='Map Y Position',
        default=0,
        help='Vertical grid position on the Warehouse Mini-Map (0 = not placed)',
    )
    zone_config_id = fields.Many2one(
        'warehouse.zone.config',
        string='Zone Config',
        ondelete='set null',
        help='Zone configuration that auto-generated this location',
    )
