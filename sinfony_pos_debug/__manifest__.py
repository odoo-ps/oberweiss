{
    'name': 'POS Virtual Printer',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'POS Virtual Printer for Debugging',
    'description': """
Instead of Printing on POS printers (normally Epson) open a browser window for 
each printer, showing what would be printed to help during developpement and
debugging.
""",
    'depends': [
        'pos_epson_printer',
    ],
    'data': [
        'views/pos_config_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_printer_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'sinfony_pos_debug/static/src/js/debug_printer.js',
            'sinfony_pos_debug/static/src/js/navbar.js',
            'sinfony_pos_debug/static/src/js/payment_screen.js',
            'sinfony_pos_debug/static/src/js/pos_printer_service.js',
            'sinfony_pos_debug/static/src/js/pos_store.js',
            'sinfony_pos_debug/static/src/js/pos_debug_button.js',
            'sinfony_pos_debug/static/src/xml/navbar.xml',
            'sinfony_pos_debug/static/src/xml/pos_debug_button.xml',
        ],
    },
    'license': 'LGPL-3',
}
