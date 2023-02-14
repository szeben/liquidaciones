# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta

class StockPickingExtendido(models.Model):
    _inherit = "stock.picking"
             
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.escribir_actividad()    
        return res

    def get_due(self, time, type_date, value_date):
        hoy = datetime.strptime(str(time), '%Y-%m-%d')
        if type_date == 'days':
            hoy += relativedelta(days =+ value_date)
        elif type_date == 'months':
            hoy += relativedelta(months =+ value_date)
        elif type_date == 'years':
            hoy += relativedelta(years =+ value_date) 
        return hoy

    def escribir_actividad(self):
        type_id = self.picking_type_id
        
        if type_id and type_id.code == 'outgoing':

            summary = type_id.activity_summary 
            tipo_act = type_id.activity_type_id 
            creador = self.user_id.id
            creador_actual = self.env['res.users'].browse(self._context.get('uid')).id
            vence_en = self.get_due(fields.Date.today(),type_id.activity_date_range,type_id.activity_time_range)

            actividad = self.env['mail.activity'].search([('res_id', '=', self.id), 
                                                          ('activity_type_id', '=', tipo_act.id)])

            self.env['mail.activity'].create({
                'note': '',
                'summary': summary,
                'date_deadline': vence_en,
                'user_id': creador if creador else creador_actual,
                'res_model_id': 406, #self.env['ir.model'].search([('model', '=', 'stock.picking')]).id
                'res_id': self.id,
                'activity_type_id': tipo_act.id
            })


