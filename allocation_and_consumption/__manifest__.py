# -*- coding: utf-8 -*-
{
    'name': "Asignación y Consumo de Equipos y Materiales",

    'summary': """
        Permite registra la asignación y consumo de equipos y materiales empleados de manera interna.
    """,

    'description': """
        Incluye movimientos de inventario y campos adicionales, 
        que permiten el registro de consumo de equipos y materiales, 
        así como la asignación de los mismos a empleados, departamentos o vehículos.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Inventory',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','branch','hr','fleet'],

    # always loaded
    'data': [
        'data/stock_locations.xml',
        'data/mov_asignacion_y_consumo.xml',
        'data/mov_asignacion.xml',
        'data/mov_consumo.xml',
        'views/stock_pick_type_views.xml',
        'views/stock_move_line_views.xml',
        'security/acceso_transferencias_internas.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
