{
    'name': 'POS Sync Performance Fixes',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Debounce the SYNCHRONISATION websocket handler and remove a duplicate ORM read in read_config_open_orders',
    'description': """
Two targeted fixes for the request storm observed on read_config_open_orders
when multiple POS terminals share the same pos.config:

1. Frontend: debounce the RPC triggered by incoming SYNCHRONISATION bus
   messages, instead of firing one read_config_open_orders call per message.
2. Backend: remove a duplicate ORM read() of the same pos.order recordset
   with the same fields inside read_config_open_orders.

Both are additive overrides, no core files are modified.
""",
    'depends': ['point_of_sale'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_sync_perf_fix/static/src/js/devices_synchronisation_patch.js',
        ],
    },
    'license': 'LGPL-3',
}
