# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from collections import OrderedDict, defaultdict
from functools import reduce
from statistics import mean, median

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
]


class StockLandedCost(models.Model):
    _name = 'pre.stock.landed.cost'
    _description = 'Stock Landed Cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Name',
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        tracking=True
    )
    date = fields.Date(
        'Date',
        default=fields.Date.context_today,
        copy=False,
        required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        tracking=True
    )

    cost_lines = fields.One2many(
        'pre.stock.landed.cost.lines',
        'cost_id',
        'Cost Lines',
        copy=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    valuation_adjustment_lines = fields.One2many(
        'pre.stock.valuation.adjustment.lines',
        'cost_id',
        'Valuation Adjustments',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    description = fields.Text(
        'Item Description',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    amount_total = fields.Monetary(
        'Total',
        compute='_compute_total_amount',
        store=True,
        tracking=True
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Posted'), ('cancel', 'Cancelled')],
        'State',
        default='draft',
        copy=False,
        readonly=True,
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.USD'),
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.company,
        required=True,
        states={'done': [('readonly', True)]}
    )
    product_lines = fields.One2many(
        'pre.stock.landed.cost.product.lines',
        'cost_id',
        string='Product Lines',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    currency_rate_usd = fields.Float(
        'Rate',
        digits=(12, 6),
        default=lambda self: self.env["res.currency"].with_context(
            date=self.date
        ).search([('name', '=', 'USD')]).inverse_rate,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    product_detail_ids = fields.One2many(
        comodel_name='pre.stock.product.detail',
        inverse_name='landed_cost_id',
        string='Detalle por producto',
        copy=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    # Detail
    total_closeouts = fields.Integer(
        string="Total de liquidaciones",
        compute="_compute_total_closeouts",
        readonly=True,
    )
    factor = fields.Float(
        string="Factor",
        compute="_compute_detail_metrics",
        readonly=True,
    )
    avg_margin = fields.Float(
        string=u"Margen promedio %",
        compute="_compute_detail_metrics",
        readonly=True,
    )
    median_margin = fields.Float(
        string=u"Margen medio %",
        compute="_compute_detail_metrics",
        readonly=True,
    )
    metrics = fields.Text(
        string="Métricas",
        compute="_compute_detail_metrics",
        readonly=True,
    )

    @api.onchange('date')
    def _onchange_date(self):
        for cost in self:
            cost.currency_rate_usd = self.env["res.currency"].with_context(
                date=cost.date
            ).search([('name', '=', 'USD')]).inverse_rate
            cost.update({"currency_rate_usd": cost.currency_rate_usd})

    @api.depends('cost_lines.price_unit')
    def _compute_total_amount(self):
        for cost in self:
            cost.amount_total = sum(line.price_unit for line in cost.cost_lines)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pre.stock.landed.cost')
        return super().create(vals)

    def unlink(self):
        self.button_cancel()
        return super().unlink()

    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'done':
            return self.env.ref('lc_pre_liquidation.mt_pre_stock_landed_cost_open')
        return super()._track_subtype(init_values)

    def button_cancel(self):
        if any(cost.state == 'done' for cost in self):
            raise UserError(_(
                'Validated landed costs cannot be cancelled, but you '
                'could create negative landed costs to reverse them'
            ))
        return self.write({'state': 'cancel'})

    def button_validate(self):
        self._check_can_validate()

        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        if cost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()

        if not self._check_sum():
            raise UserError(_(
                'Cost and adjustments lines do not match. '
                'You should maybe recompute the landed costs.'
            ))

        self.write({'state': 'done'})

        return True

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        # TODO: this should be done in batch
        for line in self.product_lines:
            if line.product_id.cost_method not in {'fifo', 'average'} or not line.quantity:
                continue

            vals = {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'former_cost': 0.0,
                'weight': line.product_id.weight * line.quantity,
                'volume': line.product_id.volume * line.quantity
            }
            lines.append(vals)

        if not lines:
            raise UserError(_(
                "You cannot apply landed costs on the chosen product_id. Landed costs "
                "can only be applied for products with FIFO or average costing method."
            ))
        return lines

    def compute_landed_cost(self):
        AdjustementLines = self.env['pre.stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        digits = 2
        towrite_dict = {}

        for cost in self:
            if not cost.product_lines:
                continue

            rounding = cost.currency_id.rounding
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()

            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['pre.stock.valuation.adjustment.lines'].create(val_line_values)

                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)

                # round this because former_cost on the valuation lines is also rounded
                total_cost += cost.currency_id.round(former_cost)
                # total_cost += tools.float_round(former_cost, precision_digits=digits) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        # if digits:
                        #     value = tools.float_round(value, precision_digits=digits, rounding_method='UP')
                        if rounding:
                            value = tools.float_round(value, precision_rounding=rounding, rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value

        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})

        detail_lines = self.env['pre.stock.product.detail']
        detail_lines.search([('landed_cost_id', 'in', self.ids)]).unlink()

        for line in self.valuation_adjustment_lines:
            if line.product_id.type != 'product':
                continue

            additional_cost = line.additional_landed_cost / line.quantity
            value = line.former_cost/line.quantity

            self.env['pre.stock.product.detail'].create({
                'name': self.name,
                'landed_cost_id': self.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'actual_cost': value,
                'additional_cost': additional_cost,
                'new_cost': value + additional_cost,
            })

        return True

    def _check_can_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))

        # TODO: check if the cost is already applied on the stock moves
        for cost in self:
            if not cost.product_lines:
                raise UserError('Agrege algunas líneas de productos.')

    def _check_sum(self):
        prec_digits = self.env.company.currency_id.decimal_places
        for landed_cost in self:
            total_amount = sum(landed_cost.valuation_adjustment_lines.mapped('additional_landed_cost'))

            if not tools.float_is_zero(total_amount - landed_cost.amount_total, precision_digits=prec_digits):
                return False

            val_to_cost_lines = defaultdict(lambda: 0.0)
            for val_line in landed_cost.valuation_adjustment_lines:
                val_to_cost_lines[val_line.cost_line_id] += val_line.additional_landed_cost

            if any(
                not tools.float_is_zero(cost_line.price_unit - val_amount, precision_digits=prec_digits)
                for cost_line, val_amount in val_to_cost_lines.items()
            ):
                return False
        return True

    @api.depends('product_lines')
    def _compute_total_closeouts(self):
        for record in self:
            record.total_closeouts = len(record.product_lines.ids)

    @api.depends('product_lines')
    def _compute_detail_metrics(self):
        for record in self:
            if self.product_lines:
                record.factor = self.product_lines[0].factor

                margin_values = self.product_lines.mapped('margin')
                record.avg_margin = mean(margin_values)
                record.median_margin = median(margin_values)

                metrics = record._get_metrics()
                record.metrics = json.dumps(
                    list(metrics.values()),
                )

            else:
                record.factor = 1.0
                record.avg_margin = 0.0
                record.median_margin = 0.0
                record.metrics = json.dumps([])

    def _get_metrics(self):
        self.ensure_one()

        price_unit_usd = self.product_lines.mapped('price_unit_usd')
        amount_total_rd = self.product_lines.mapped('amount_total_rd')

        current_total_usd = self.product_lines.mapped('current_total_usd')
        current_total_rd = self.product_lines.mapped('current_total_rd')

        pvp_usd = self.product_lines.mapped('pvp_usd')
        pvp_rd = self.product_lines.mapped('pvp_rd')

        profit_usd = self.product_lines.mapped('profit_usd')
        profit_rd = self.product_lines.mapped('profit_rd')

        return OrderedDict([
            ("total_fob", {
                "string": "Total FOB",
                "usd": sum(price_unit_usd),
                "rd": sum(amount_total_rd)
            }),
            ("current_total_cost", {
                "string": "Costo Total Actual",
                "usd": sum(current_total_usd),
                "rd": sum(current_total_rd)
            }),
            ("avg_pvp", {
                "string": "PVP Promedio",
                "usd": mean(pvp_usd),
                "rd": mean(pvp_rd)
            }),
            ("median_pvp", {
                "string": "PVP Media",
                "usd": median(pvp_usd),
                "rd": median(pvp_rd)
            }),
            ("total_profit", {
                "string": "Total Ganancia",
                "usd": sum(profit_usd),
                "rd": sum(profit_rd)
            })
        ])

    def action_view_closeouts_detail(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "lc_pre_liquidation.pre_stock_landed_cost_product_lines_action_window"
        )
        return dict(
            action,
            view_type='list',
            domain=[('id', 'in', self.product_lines.ids)],
            context=self.env.context
        )
