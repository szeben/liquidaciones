# -*- coding: utf-8 -*-
from odoo import api, fields, models

class OperationTypeExtendida(models.Model):
    _inherit = "stock.picking.type"

    asignacion_y_consumo_interno = fields.Boolean(string="¿Es para asignación y consumo interno?")