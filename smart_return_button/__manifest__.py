# -*- coding: utf-8 -*-
{
    'name': "Botón Inteligente para Devoluciones",

    'summary': """
        Limita la visibilidad del botón de envío para solo OS facturadas. Incluye botón inteligente para devoluciones. 
    """,

    'description': """
        Limita la visibilidad del botón de envío para solo algunos usuarios y si la OS se encuentra facturada. 
        Incluye un nuevo botón para Devoluciones, visible solo para algunos usuarios y si la OS se encuentra facturada. 
        Crea grupos de usuarios para la visibilidad de los botones.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Sales',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock'],

    # always loaded
    'data': [
        'security/despacho_devolucion.xml',
        'views/despacho_devolucion_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
