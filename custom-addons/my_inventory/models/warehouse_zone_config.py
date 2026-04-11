from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WarehouseZoneConfig(models.Model):
    _name = 'warehouse.zone.config'
    _description = 'Warehouse Zone Configuration'
    _order = 'sequence, name'

    name = fields.Char(string='Zone Name', required=True)
    sequence = fields.Integer(default=10)
    num_rows = fields.Integer(string='Number of Rows', default=2)
    num_shelves = fields.Integer(string='Shelves per Row', default=5)
    capacity = fields.Integer(string='Max Units per Shelf', default=100)
    active = fields.Boolean(default=True)
    location_ids = fields.One2many(
        'stock.location', 'zone_config_id', string='Generated Locations'
    )

    def action_generate_layout(self):
        for config in self:
            existing = config.location_ids
            if existing:
                quants = self.env['stock.quant'].search([
                    ('location_id', 'in', existing.ids),
                    ('quantity', '>', 0),
                ])
                if quants:
                    raise UserError(_(
                        'Cannot regenerate "%s": some locations still have stock. '
                        'Transfer or clear all stock first.'
                    ) % config.name)
                existing.with_context(active_test=False).unlink()
            config._create_locations()

    def _create_locations(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if not warehouse:
            raise UserError(_('No warehouse found. Please configure a warehouse first.'))
        stock_loc = warehouse.lot_stock_id

        # Check if zone parent location already exists
        zone_loc = self.env['stock.location'].search([
            ('zone_config_id', '=', self.id),
            ('x_pos', '=', 0),
            ('y_pos', '=', 0),
        ], limit=1)

        if not zone_loc:
            zone_loc = self.env['stock.location'].create({
                'name': self.name,
                'location_id': stock_loc.id,
                'usage': 'internal',
                'x_pos': 0,
                'y_pos': 0,
                'zone_config_id': self.id,
            })

        # X offset: sum of num_rows from all active configs with lower sequence
        earlier = self.env['warehouse.zone.config'].search([
            '|',
            ('sequence', '<', self.sequence),
            '&', ('sequence', '=', self.sequence), ('id', '<', self.id),
            ('active', '=', True),
        ])
        x_base = sum(z.num_rows for z in earlier)

        for r in range(1, self.num_rows + 1):
            row_x = x_base + r
            row_loc = self.env['stock.location'].create({
                'name': 'Row %d' % r,
                'location_id': zone_loc.id,
                'usage': 'internal',
                'x_pos': row_x,
                'y_pos': 2,
                'zone_config_id': self.id,
            })
            for s in range(1, self.num_shelves + 1):
                self.env['stock.location'].create({
                    'name': 'Shelf %d' % s,
                    'location_id': row_loc.id,
                    'usage': 'internal',
                    'x_pos': row_x,
                    'y_pos': 3,
                    'zone_config_id': self.id,
                })
