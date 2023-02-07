# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductTemplateExtendido(models.Model):
    _inherit = "product.template"

    precios_extras_ids = fields.One2many(string='Precios Extras', 
                                         inverse_name="product_tmpl_id",
                                         comodel_name="product.pricelist.item")
    

class ProductProductExtendido(models.Model):
    _inherit = "product.product"

    precios_extras_ids = fields.One2many(string='Precios Extras', 
                                         inverse_name="product_id",
                                         comodel_name="product.pricelist.item")

