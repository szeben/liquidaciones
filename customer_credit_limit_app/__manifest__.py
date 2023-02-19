# -*- coding: utf-8 -*-

{
    "name" : "Customer Credit Limit",
    "author": "Edge Technologies",
    "version" : "16.0.1.0",
    "live_test_url":'https://youtu.be/6Gk6vhIBF2s',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Credit limit for customer credit limit credit limit for customer credit limit with due amount warning customers credit limit check customer credit limit exceeded customer credit limit on hold customer account limit credit account limit partner credit limit',
    "description": """
    
  This app used to set credit limit for each customer, based on that approval is required on sales order. configuration is available to create delivery order before or after credit limit approval. customer due invoice approval on sales order also possible with this odoo module. 
credit limit for customer credit limit credit limit for individual customers cc hold cc payment cc customer credit limit with due amount warning credit limit feature customer credit limit with warning delivery customers credit limit check customer credit limit credit limit amount 
customer credit limit exceeded credit limit customer on credit limit hold credit limit on hold customer account limit credit account limit 
credit account hold hold credit account 

    
    """,
    "license" : "OPL-1",
    "depends" : ['base','sale_management','account','stock','sale_stock'],
    "data": [
        'security/groups.xml',
        'views/config_views.xml',
        'views/sale_view_inherit.xml',
        'views/res_partner_inherit.xml',
        'views/picking_inherit_view.xml',
        
    ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": 'EUR',
    "category" : "Sales",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
