# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class AdjustmentLines(models.Model):
    _name = 'pre.stock.valuation.adjustment.lines'
    _description = 'Stock Valuation Adjustment Lines'
    _inherit = 'stock.valuation.adjustment.lines'

    cost_id = fields.Many2one(
        'pre.stock.landed.cost',
        string='Landed Cost',
        ondelete='cascade', required=True
    )
    cost_line_id = fields.Many2one(
        'pre.stock.landed.cost.lines',
        string='Cost Line',
        readonly=True
    )
    additional_landed_cost = fields.Monetary(
        string='Additional Landed Cost'
    )

    @api.model
    def _add_field(self, name, field):
        if name == 'move_id':
            return
        return super()._add_field(name, field)
