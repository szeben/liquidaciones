# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from collections import defaultdict


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    additional_landed_cost = fields.Monetary(string='Additional Landed Cost')
    picking_id = fields.Many2one('stock.picking', string='Transferencia', readonly=True)


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    product_detail_ids = fields.One2many(
        comodel_name='stock.product.detail',
        inverse_name='landed_cost_id',
        string='Detalle por producto',
        copy=False)

    NumeroDeclaracion = fields.Char(string='Numero de declaracion')
    NumeroManifiesto = fields.Char(string='Numero de manifiesto')
    ValoracionCIF = fields.Float(string='Valoracion CIF')
    BlNum = fields.Char(string='Numero de BL')
    FurgonNum = fields.Char(string='Numero de Furgon')
    NumSellos = fields.Char(string='Numero de Sellos')
    TotalGravamen = fields.Float(string='Total de gravamen')
    TotalItbis = fields.Float(string='Total de ITBIS')
    TipoImportacion = fields.Selection(string='Tipo de Importación', selection=[('Local', 'Exterior')])

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        for move in self._get_targeted_move_ids():
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.cost_method not in ('fifo', 'average') or move.state == 'cancel' or not move.product_qty:
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty,
                'picking_id': move.picking_id.id,
            }
            lines.append(vals)

        if not lines:
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            raise UserError(_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.",
                            target_model_descriptions[self.target_model]))
        return lines

    def compute_landed_cost(self):
        result = super(StockLandedCost, self).compute_landed_cost()
        digits = 2
        detail_lines = self.env['stock.product.detail']
        detail_lines.search([('landed_cost_id', 'in', self.ids)]).unlink()

        details = defaultdict(lambda: {})

        for line in self.valuation_adjustment_lines:
            if line.product_id.type != 'product':
                continue

            additional_cost = line.additional_landed_cost / line.quantity

            product_id = line.product_id.id
            picking_id = line.picking_id.id

            if product_id not in details[picking_id]:
                value = line.former_cost / line.quantity

                details[picking_id][product_id] = {
                    'name': self.name,
                    'landed_cost_id': self.id,
                    'product_id': product_id,
                    'quantity': line.quantity,
                    'actual_cost': value,
                    'additional_cost': additional_cost,
                    'new_cost': value + additional_cost,
                }

            else:
                details[picking_id][product_id]['additional_cost'] += additional_cost
                details[picking_id][product_id]['new_cost'] += additional_cost

        for data_pickinds in details.values():
            for data_product in data_pickinds.values():
                self.env['stock.product.detail'].create(data_product)

        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        digits = 2
        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits) if digits else former_cost

                total_line += 1

            for line_cost in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line_cost.id:
                        if line_cost.split_method == 'by_quantity' and total_qty:
                            per_unit = (line_cost.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line_cost.split_method == 'by_weight' and total_weight:
                            per_unit = (line_cost.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line_cost.split_method == 'by_volume' and total_volume:
                            per_unit = (line_cost.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line_cost.split_method == 'equal':
                            value = (line_cost.price_unit / total_line)
                        elif line_cost.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line_cost.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line_cost.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits, rounding_method='UP')
                            fnc = min if line_cost.price_unit > 0 else max
                            value = fnc(value, line_cost.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value

        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})

        return result


class StockProductDetail(models.Model):
    _name = 'stock.product.detail'
    _description = 'Stock Landed Cost Product Details'

    name = fields.Char(u'Descripción', required=True)
    landed_cost_id = fields.Many2one(
        comodel_name='stock.landed.cost',
        string=u'Liquidación',
        ondelete='cascade',
        required=True)
    product_id = fields.Many2one('product.product', 'Producto', required=True)
    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    actual_cost = fields.Float(
        'Costo actual unitario',
        readonly=True)

    additional_cost = fields.Float(
        string=u'Costo de Importación',
        readonly=True)

    new_cost = fields.Float(
        string=u'Nuevo Costo',
        readonly=True)
