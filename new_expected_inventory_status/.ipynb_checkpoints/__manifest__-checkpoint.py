# -*- coding: utf-8 -*-
{
    'name': "Nuevo Estado de Inventario Pronosticado",

    'summary': """
        Modifica el icono de inventario pronosticado en la orden de venta para considerar un cumplimiento parcial de un pedido.
    """,

    'description': """
        Modifica el icono de inventario pronosticado en la orden de venta para considerar un cumplimiento parcial de un pedido.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Sales',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_stock'],

    # always loaded
    'data': [
        'views/sale_stock_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'new_expected_inventory_status/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'new_expected_inventory_status/static/src/xml/**/*',
        ],
    },
}
