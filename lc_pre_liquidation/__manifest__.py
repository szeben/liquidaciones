# -*- coding: utf-8 -*-
{
    'name': "Preliquidaciones",

    'summary': """
        Incluye en el módulo de compras un simulador para el cálculo 
        de coste en destino o liquidaciones, sin afectación en 
        inventario, ni afectación contable.""",

    'description': """
        Incluye en el módulo de compras un simulador para el cálculo de 
        coste en destino o liquidaciones, sin afectación en inventario, 
        ni afectación contable.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_landed_costs', 'lc_detail_and_indicators'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/stock_landed_cost_security.xml',
        'data/stock_landed_cost_data.xml',
        'views/stock_landed_cost_views.xml',
        'views/stock_landed_cost_detail_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
