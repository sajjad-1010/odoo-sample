from odoo import http
from odoo.http import request


class WarehouseMinimapController(http.Controller):

    @http.route('/warehouse_minimap/data', type='json', auth='user', methods=['POST'])
    def get_minimap_data(self):
        Location = request.env['stock.location']
        Quant = request.env['stock.quant']

        locations = Location.search([
            ('usage', '=', 'internal'),
            ('x_pos', '!=', 0),
            ('y_pos', '!=', 0),
        ])

        quants = Quant.search_read(
            domain=[('location_id', 'in', locations.ids), ('quantity', '>', 0)],
            fields=['location_id', 'product_id', 'quantity'],
        )

        quants_by_location = {}
        for q in quants:
            loc_id = q['location_id'][0]
            if loc_id not in quants_by_location:
                quants_by_location[loc_id] = []
            quants_by_location[loc_id].append({
                'product_name': q['product_id'][1],
                'quantity': q['quantity'],
            })

        result = []
        for loc in locations:
            result.append({
                'id': loc.id,
                'name': loc.complete_name,
                'x': loc.x_pos,
                'y': loc.y_pos,
                'zone_config_id': loc.zone_config_id.id if loc.zone_config_id else False,
                'products': quants_by_location.get(loc.id, []),
            })

        return result

    @http.route('/warehouse_minimap/zones', type='json', auth='user', methods=['POST'])
    def get_zone_configs(self):
        ZoneConfig = request.env['warehouse.zone.config']
        Location = request.env['stock.location']
        Quant = request.env['stock.quant']

        configs = ZoneConfig.search([('active', '=', True)], order='sequence, name')
        if not configs:
            return []

        # All locations belonging to any config
        all_locs = Location.search([('zone_config_id', 'in', configs.ids)])

        # Collect quants for all leaf locations
        quants = Quant.search_read(
            domain=[('location_id', 'in', all_locs.ids), ('quantity', '>', 0)],
            fields=['location_id', 'product_id', 'quantity'],
        )
        quants_by_loc = {}
        for q in quants:
            lid = q['location_id'][0]
            quants_by_loc.setdefault(lid, []).append({
                'product_name': q['product_id'][1],
                'quantity': q['quantity'],
            })

        result = []
        for config in configs:
            # Zone parent = location with x_pos=0 belonging to this config
            zone_loc = Location.search([
                ('zone_config_id', '=', config.id),
                ('x_pos', '=', 0),
            ], limit=1)

            if not zone_loc:
                result.append({
                    'id': config.id, 'name': config.name,
                    'num_rows': config.num_rows, 'num_shelves': config.num_shelves,
                    'capacity': config.capacity, 'rows': [],
                })
                continue

            # Direct children of zone parent
            direct_children = Location.search([
                ('location_id', '=', zone_loc.id),
                ('zone_config_id', '=', config.id),
                ('usage', '=', 'internal'),
            ], order='x_pos, name')

            # Detect 2-level vs 3-level:
            # 3-level: direct children have their own children (rows → shelves)
            # 2-level: direct children ARE the shelves (legacy style)
            has_grandchildren = any(
                Location.search_count([
                    ('location_id', '=', child.id),
                    ('zone_config_id', '=', config.id),
                ]) > 0
                for child in direct_children
            )

            rows = []
            if has_grandchildren:
                # 3-level structure (created via Generate Layout)
                for row_loc in direct_children:
                    shelf_locs = Location.search([
                        ('location_id', '=', row_loc.id),
                        ('zone_config_id', '=', config.id),
                    ], order='name')
                    shelves = [{
                        'id': s.id,
                        'name': s.name,
                        'full_path': s.complete_name,
                        'products': quants_by_loc.get(s.id, []),
                        'capacity': config.capacity,
                    } for s in shelf_locs]
                    rows.append({'id': row_loc.id, 'name': row_loc.name, 'shelves': shelves})
            else:
                # 2-level structure (legacy/migrated zones)
                # Direct children are the shelf cells; group them in a single virtual row
                shelves = [{
                    'id': leaf.id,
                    'name': leaf.name,
                    'full_path': leaf.complete_name,
                    'products': quants_by_loc.get(leaf.id, []),
                    'capacity': config.capacity,
                } for leaf in direct_children]
                if shelves:
                    rows = [{'id': -config.id, 'name': '', 'shelves': shelves}]

            result.append({
                'id': config.id,
                'name': config.name,
                'num_rows': config.num_rows,
                'num_shelves': config.num_shelves,
                'capacity': config.capacity,
                'rows': rows,
            })

        return result
