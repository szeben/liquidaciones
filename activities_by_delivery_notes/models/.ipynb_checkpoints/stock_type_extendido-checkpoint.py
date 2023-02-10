# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class StockTypeExtendido(models.Model):
    _inherit = "stock.picking.type"
    
    """
    @api.depends('mail_act')
    def _default_user(self):
        usuario = self._env['res.user'].browse()
        self.stock_activity_user.type = 'generic'
        #self.stock_activiry_user.name = 
    """

    mail_act = fields.Many2one(comodel_name="mail.activity", string="Actividad")
    
    #stock_activity_res = fields.Char(related="mail_act.res_model", string="Modelo de Actividad", store=True, readonly=True)
    activity_type = fields.Many2one(related="mail_act.activity_type_id", string="Tipo de Actividad", store=True, readonly=False, domain=['|', ('res_model', '=', False), ('res_model', '=', 'stock.picking.type')])
    activity_summary = fields.Char(related="mail_act.summary", string="Resumen", store=True, readonly=False)
    activity_date = fields.Date(related="mail_act.date_deadline", string="Fecha de Vencimiento", store=True)
    #activity_user = fields.Many2one(related="mail_act.date_deadline", string="Fecha de Vencimiento", store=True, compute='_default_user')
    
    activity_date_range = fields.Selection([
        ('days', 'Días'),
        ('months', 'Meses'),
        ('years', 'Años')], 
        default="days",
        required=True,
    )
    
    activity_time_range = fields.Integer(default=1, string="Fecha de Vencimiento en", required=True)
    
    #Máximo 5 años
    @api.constrains('activity_time_range', 'activity_date_range')
    def _check_activity_time_range(self):
        for record in self:
            date = record.activity_date_range
            time = record.activity_time_range
            if time < 1:
                record.activity_time_range = (abs(record.activity_time_range))
            else:
                if date == 'days' and time > 1826:
                    raise ValidationError('Rango de días inválido (hasta 5 años).')
                elif date == 'months' and time > 60:
                    raise ValidationError('Rango de meses inválido (hasta 5 años).')
                elif date == 'years' and time > 5:
                    raise ValidationError('Rango de años inválido (hasta 5 años).') 
                    
                    
    @api.onchange('activity_time_range','activity_date_range')
    def _onchange_range(self):
        actual = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        if self.activity_date_range == 'days':
            self.activity_date = (actual+relativedelta(days =+ self.activity_time_range)).strftime('%Y-%m-%d')
        elif self.activity_date_range == 'months':
            self.activity_date = (actual+relativedelta(months =+ self.activity_time_range)).strftime('%Y-%m-%d')
        elif self.activity_date_range == 'years':
            self.activity_date = (actual+relativedelta(years =+ self.activity_time_range)).strftime('%Y-%m-%d')
            
    

                
                
                
                
                   
    
  


