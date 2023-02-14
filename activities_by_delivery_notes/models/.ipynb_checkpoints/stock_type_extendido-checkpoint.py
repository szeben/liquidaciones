# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class StockTypeExtendido(models.Model):
    _inherit = "stock.picking.type"
    
    #ids / info
    mail_act = fields.Many2one(comodel_name="mail.activity", string="Actividad")
    #activity_res_model_id = fields.Char(related="mail_act.res_model_id", store=True, readonly=False)
    activity_type_id = fields.Many2one(related='mail_act.activity_type_id', string='Tipo de Actividad',
                                       store=True, readonly=False,
                                       domain="['|', ('res_model', '=', False), ('res_model', '=', 'stock.picking')]")

    activity_summary = fields.Char(related="mail_act.summary", string="Resumen", store=True, readonly=False)
    
    
    #dates
    activity_date = fields.Date(related="mail_act.date_deadline", string="Fecha de Vencimiento", store=True, readonly=False, default=datetime.strptime(str(fields.Date.today()), '%Y-%m-%d'))
    activity_time_range = fields.Integer(default=1, string="Fecha de Vencimiento en")
    activity_date_range = fields.Selection([
        ('days', 'Día(s)'),
        ('months', 'Mes(es)'),
        ('years', 'Año(s)')], 
        default="days",
    )

    
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
                    


    
    # user
    #activity_user = fields.Many2one('mail_act.user_id', default=lambda self: self.env.user, index=True)

                
                
                
                
                   
    
  


