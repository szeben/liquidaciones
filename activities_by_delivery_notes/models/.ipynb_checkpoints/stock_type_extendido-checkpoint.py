# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class StockTypeExtendido(models.Model):
    _inherit = "stock.picking.type"
    
    #ids / info
    mail_act = fields.Many2one(comodel_name="mail.activity", string="Actividad")
    #activity_res_model = fields.Char(related="mail_act.res_model", store=True, readonly=False)
    activity_type_id = fields.Many2one(related='mail_act.activity_type_id', string='Tipo de Actividad',
                                       store=True, readonly=False,
                                       domain="['|', ('res_model', '=', False), ('res_model', '=', 'stock.picking.type')]")

    activity_summary = fields.Char(related="mail_act.summary", string="Resumen", store=True, readonly=False)
    
    
    #dates
    activity_date = fields.Date(related="mail_act.date_deadline", string="Fecha de Vencimiento", store=True, readonly=False)
    activity_time_range = fields.Integer(default=1, string="Fecha de Vencimiento en", required=True)
    activity_date_range = fields.Selection([
        ('days', 'Día(s)'),
        ('months', 'Mes(es)'),
        ('years', 'Año(s)')], 
        default="days",
        required=True,
    )
    
    def _return_selection(self):
        return dict(self._fields['activity_date_range'].selection).get(self.activity_date_range)
    
    @api.onchange('activity_time_range')
    def _onchange_activity_time_range(self):
        if self.activity_time_range < 0:
            raise ValidationError("La fecha de vencimiento no puede ser negativa.")
    
    
    #Máximo 5 años
    @api.constrains('activity_time_range', 'activity_date_range')
    def _check_activity_time_range(self):
        for record in self:
            date = record.activity_date_range
            time = record.activity_time_range
            if date == 'days' and time > 1826:
                raise ValidationError('Rango de días inválido (hasta 5 años).')
            elif date == 'months' and time > 60:
                raise ValidationError('Rango de meses inválido (hasta 5 años).')
            elif date == 'years' and time > 5:
                raise ValidationError('Rango de años inválido (hasta 5 años).') 
                    
                    
    @api.onchange('activity_time_range','activity_date_range')
    def _onchange_range(self):
        self.activity_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        if self.activity_date_range == 'days':
            self.activity_date += relativedelta(days =+ self.activity_time_range)
        elif self.activity_date_range == 'months':
            self.activity_date += relativedelta(months =+ self.activity_time_range)
        elif self.activity_date_range == 'years':
            self.activity_date += relativedelta(years =+ self.activity_time_range)
                
    
    #user   
    activity_user_field_name = fields.Char('Usuario', default="user_id", required=True, store=True)
    activity_user_type = fields.Selection([
        ('specific', 'Specific User'),
        ('generic', 'Generic User From Record')], default="specific", required=True, store=True)
    

    

                
                
                
                
                   
    
  


