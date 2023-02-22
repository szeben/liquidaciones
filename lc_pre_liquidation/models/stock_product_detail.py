# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockProductDetail(models.Model):
    _name = 'pre.stock.product.detail'
    _description = 'Stock Landed Cost Product Details'

    name = fields.Char(
        string=u'Descripción',
        required=True
    )
    landed_cost_id = fields.Many2one(
        comodel_name='pre.stock.landed.cost',
        string=u'Pre liquidación',
        ondelete='cascade',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto'
    )
    description = fields.Char(
        string='Descripción'
    )
    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits=dp.get_precision('Product Unit of Measure'),
        required=True
    )
    actual_cost = fields.Monetary(
        string='Costo actual unitario USD',
        readonly=True
    )
    additional_cost = fields.Monetary(
        string=u'Costo de Importación USD',
        readonly=True
    )
    new_cost = fields.Monetary(
        string=u'Nuevo Costo USD',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='landed_cost_id.currency_id'
    )
