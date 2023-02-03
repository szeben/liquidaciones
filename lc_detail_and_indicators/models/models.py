# -*- coding: utf-8 -*-

import json
from functools import reduce
from statistics import mean, median
from collections import OrderedDict

from odoo import api, fields, models


class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=[('list', 'List')],
        ondelete={'list': 'cascade'},
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    item = fields.Integer(
        string="Item",
        compute="_compute_totals",
        readonly=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de compra',
        compute="_compute_info_purchase",
        store=True,
        readonly=True,
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        compute="_compute_info_purchase",
        store=True,
        readonly=True,
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string='Facturas',
        compute="_compute_info_purchase",
        store=True,
        readonly=True,
        domain=[('move_type', '=', 'in_invoice')]
    )
    currency_date_rate = fields.Date(
        string="Fecha tasa",
        compute="_compute_rate_usd",
        readonly=True,
    )
    currency_rate_usd = fields.Float(
        string="Tasa USD",
        compute="_compute_rate_usd",
        readonly=True,
    )
    price_unit_usd = fields.Float(
        string="C/U US$",
        compute="_compute_totals",
        readonly=True,
    )
    amount_total_usd = fields.Float(
        string="Total US$",
        compute="_compute_totals",
        readonly=True,
    )
    price_unit_rd = fields.Float(
        string="C/U RD",
        compute="_compute_totals",
        readonly=True,
    )
    amount_total_rd = fields.Float(
        string="Total RD",
        compute="_compute_totals",
        readonly=True,
    )
    factor = fields.Float(
        string="Factor",
        compute="_compute_factor",
        readonly=True,
    )
    current_price_unit_rd = fields.Float(
        string="C/U Actual RD",
        compute="_compute_current_totals",
        readonly=True,
    )
    current_total_rd = fields.Float(
        string="C/T Actual RD",
        compute="_compute_current_totals",
        readonly=True,
    )
    current_price_unit_usd = fields.Float(
        string="C/U Actual US$",
        compute="_compute_current_totals",
        readonly=True,
    )
    current_total_usd = fields.Float(
        string="C/T Actual US$",
        compute="_compute_current_totals",
        readonly=True,
    )
    pvp_usd = fields.Float(
        string="PVP US$",
        default=lambda self: self.product_id.lst_price * self.env.ref('base.USD').inverse_rate,
    )
    pvp_rd = fields.Float(
        string="PVP RD",
        compute="_compute_pvp",
        compute_sudo=True,
        readonly=True,
    )
    margin = fields.Float(
        string="Margen %",
        compute="_compute_extra_indicators",
        readonly=True,
    )
    profit_usd = fields.Float(
        string="Ganancias en US$",
        compute="_compute_extra_indicators",
        readonly=True,
    )
    profit_rd = fields.Float(
        string="Ganancias en RD",
        compute="_compute_extra_indicators",
        readonly=True,
    )

    @api.depends_context('landed_cost_date', 'date')
    def _compute_rate_usd(self):
        date = (
            self._context.get('landed_cost_date')
            or self._context.get('date')
            or fields.Date.today()
        )
        self.currency_date_rate = date
        self.currency_rate_usd = self.env["res.currency"].with_context({
            'date': date,
        }).search([("name", "=", "USD")]).inverse_rate

    @api.depends('picking_id', 'picking_id.purchase_id', 'picking_id.purchase_id.invoice_ids', 'purchase_line_id.order_id')
    def _compute_info_purchase(self):
        for record in self:
            if record.purchase_line_id and record.purchase_line_id.order_id:
                record.purchase_order_id = record.purchase_line_id.order_id
            else:
                record.purchase_order_id = record.picking_id.purchase_id
            record.invoice_ids = record.picking_id.purchase_id.invoice_ids
            record.supplier_id = record.picking_id.partner_id

    @api.depends('currency_rate_usd', 'price_unit', 'product_uom_qty', 'purchase_order_id')
    def _compute_totals(self):
        for item, record in enumerate(self, start=1):
            record.item = item

            if record.purchase_order_id and record.purchase_order_id.currency_rate:
                record.price_unit_rd = record.price_unit / record.purchase_order_id.currency_rate
            else:
                record.price_unit_rd = record.price_unit

            record.price_unit_usd = record.price_unit_rd / record.currency_rate_usd
            record.amount_total_usd = record.price_unit_usd * record.product_uom_qty
            record.amount_total_rd = record.price_unit_rd * record.product_uom_qty

    @api.depends('amount_total_usd', 'amount_total_rd')
    @api.depends_context('landed_cost_id', 'active_id')
    def _compute_factor(self):
        landed_cost = self.env['stock.landed.cost'].browse(
            self._context.get('landed_cost_id') or self._context.get('active_id')
        )

        if landed_cost:
            stock_move_ids = self.browse(
                landed_cost._get_move_ids_without_package().ids
            )
            total_usd = sum(stock_move_ids.mapped('amount_total_usd'))
            total_rd = sum(stock_move_ids.mapped('amount_total_rd'))
            if total_usd:
                self.factor = (landed_cost.amount_total + total_rd) / total_usd
            else:
                self.factor = 1.0
        else:
            self.factor = 1.0

    @api.depends('currency_rate_usd', 'factor')
    def _compute_current_totals(self):
        for record in self:
            record.current_price_unit_rd = record.price_unit_rd * record.factor
            record.current_total_rd = record.current_price_unit_rd * record.product_uom_qty
            record.current_price_unit_usd = (
                record.current_price_unit_rd / record.currency_rate_usd
                if record.currency_rate_usd else 0.0
            )
            record.current_total_usd = record.current_price_unit_usd * record.product_uom_qty

    @api.depends('currency_rate_usd', 'pvp_usd')
    def _compute_pvp(self):
        for record in self:
            record.pvp_rd = record.pvp_usd * record.currency_rate_usd

    @api.depends('pvp_usd', 'pvp_rd', 'current_price_unit_usd', 'current_price_unit_rd', 'product_uom_qty')
    def _compute_extra_indicators(self):
        for record in self:
            if record.pvp_usd:
                record.margin = (record.pvp_usd - record.current_price_unit_usd) * 100 / record.pvp_usd
            else:
                record.margin = 0.0
            record.profit_usd = (record.pvp_usd - record.current_price_unit_usd) * record.product_uom_qty
            record.profit_rd = (record.pvp_rd - record.current_price_unit_rd) * record.product_uom_qty

    def get_lst_price_from_product(self, vals):
        product = self.env['product.product'].browse(vals.get('product_id'))
        return (product.lst_price or 0.0) * self.env.ref('base.USD').inverse_rate

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list['pvp_usd'] = self.get_lst_price_from_product(vals_list)
        else:
            for vals in vals_list:
                vals['pvp_usd'] = self.get_lst_price_from_product(vals)
        return super().create(vals_list)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    landed_costs_ids = fields.Many2many(
        'stock.landed.cost',
        string='Costes de destino',
        copy=False
    )


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    total_closeouts = fields.Integer(
        string="Total de liquidaciones",
        compute="_compute_total_closeouts",
        readonly=True,
    )
    currency_rate_usd = fields.Float(
        string="Tasa de cambio",
        compute="_compute_currency_rate_usd",
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

    @api.depends('picking_ids')
    def _compute_total_closeouts(self):
        for record in self:
            record.total_closeouts = len(record._get_move_ids_without_package().ids)

    @api.depends('date')
    def _compute_currency_rate_usd(self):
        for record in self:
            record.currency_rate_usd = self.env["res.currency"].with_context({
                'date': record.date,
            }).browse(self.env.ref('base.USD').id).inverse_rate

    def _get_stock_moves(self) -> 'StockMove':
        self.ensure_one()
        return self.env['stock.move'].with_context({
            "landed_cost_id": self.id,
            "landed_cost_date": self.date
        }).browse(self._get_move_ids_without_package().ids)

    @api.depends('picking_ids')
    def _compute_detail_metrics(self):
        for record in self:
            stock_moves = record._get_stock_moves()

            if stock_moves:
                record.factor = stock_moves[0].factor

                margin_values = stock_moves.mapped('margin')
                record.avg_margin = mean(margin_values)
                record.median_margin = median(margin_values)

                metrics = record._get_metrics(stock_moves)
                record.metrics = json.dumps(
                    list(metrics.values()),
                )

            else:
                record.factor = 1.0
                record.avg_margin = 0.0
                record.median_margin = 0.0
                record.metrics = json.dumps([])

    def _get_metrics(self, stock_moves=None) -> OrderedDict:
        self.ensure_one()
        stock_moves = stock_moves or self._get_stock_moves()

        amount_total_usd = stock_moves.mapped('amount_total_usd')
        amount_total_rd = stock_moves.mapped('amount_total_rd')

        current_total_usd = stock_moves.mapped('current_total_usd')
        current_total_rd = stock_moves.mapped('current_total_rd')

        pvp_usd = stock_moves.mapped('pvp_usd')
        pvp_rd = stock_moves.mapped('pvp_rd')

        profit_usd = stock_moves.mapped('profit_usd')
        profit_rd = stock_moves.mapped('profit_rd')

        return OrderedDict([
            ("total_fob", {
                "string": "Total FOB",
                "usd": sum(amount_total_usd),
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

    def _get_move_ids_without_package(self):
        self.ensure_one()
        return reduce(
            lambda p1, p2: p1 | p2.move_ids_without_package,
            self.picking_ids,
            self.env["stock.move"]
        )

    def action_view_closeouts_detail(self):
        move_ids = self._get_move_ids_without_package().ids
        action = self.env["ir.actions.actions"]._for_xml_id(
            "lc_detail_and_indicators.closeouts_detail_action_window"
        )
        return dict(
            action,
            view_type='list',
            domain=[('id', 'in', move_ids)],
            context=dict(
                self.env.context,
                landed_cost_id=self.id,
                landed_cost_date=self.date
            )
        )
