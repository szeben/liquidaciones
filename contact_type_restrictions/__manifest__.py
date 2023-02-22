# -*- coding: utf-8 -*-
{
    'name': "contact_type_restrictions",

    'summary': """
        Restringe la visualizacion y gestión de los contactos de acuerdo a su clasificación
        como cliente o proveedor""",

    'description': """
        Restringe la posibilidad de crear contactos de acuerdo a su clasificación como
        cliente o proveedor. Restringe la visualización de contactos de tipo proveedor y proveedores
        nacionales. Restringe la visualización de contactos de tipo cliente.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Ventas',
    'version': '0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'sale', 'account'],

    # always loaded
    'data': [
        'security/contact_type_restrictions_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "auto_install": False,
    "installable": True,

    "uninstall_hook": 'contact_type_restrictions_uninstall_hook',
}
