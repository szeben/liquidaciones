# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockMoveLineExtendida(models.Model):
    _inherit = "stock.move.line"
    
    hr_department_id = fields.Many2one(string="Departamento",comodel_name="hr.department")
    hr_employee_id = fields.Many2one(string="Empleado",comodel_name="hr.employee")
    fleet_vehicle_id = fields.Many2one(string="Vehículo",comodel_name="fleet.vehicle")
