# -*- coding: utf-8 -*-
# from odoo import http


# class ContactTypeRestrictions(http.Controller):
#     @http.route('/contact_type_restrictions/contact_type_restrictions', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_type_restrictions/contact_type_restrictions/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_type_restrictions.listing', {
#             'root': '/contact_type_restrictions/contact_type_restrictions',
#             'objects': http.request.env['contact_type_restrictions.contact_type_restrictions'].search([]),
#         })

#     @http.route('/contact_type_restrictions/contact_type_restrictions/objects/<model("contact_type_restrictions.contact_type_restrictions"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_type_restrictions.object', {
#             'object': obj
#         })
