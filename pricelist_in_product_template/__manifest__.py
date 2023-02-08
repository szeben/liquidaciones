# -*- coding: utf-8 -*-
{
    'name': "Precios extras desde plantilla de producto",

    'summary': """
        Incluye la lista de precios dentro de la ficha de información del producto.
    """,

    'description': """
        Incluye la lista de precios dentro de la ficha de información del producto, permitiendo que se puedan modificar o incluir desde ese nuevo espacio.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Inventory',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        'views/precios_extras_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
