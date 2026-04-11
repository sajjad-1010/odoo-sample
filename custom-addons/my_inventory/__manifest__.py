{
    'name': 'My Inventory',
    'version': '17.0.1.1.0',
    'summary': 'Custom Inventory Module with Warehouse Mini-Map',
    'category': 'Inventory',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['stock', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml',
        'views/stock_location_views.xml',
        'views/warehouse_minimap_views.xml',
        'views/warehouse_zone_config_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_inventory/static/src/js/minimap_widget.js',
            'my_inventory/static/src/xml/minimap_widget.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
