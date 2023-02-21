# -*- coding: utf-8 -*-

from odoo import fields,models,api, _
from ast import literal_eval
from odoo import SUPERUSER_ID
from odoo.http import request


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    due_date_check = fields.Boolean(string="Due Date",related="company_id.due_date_check",readonly=False)
    sale_approve = fields.Selection(related="company_id.sale_approve",readonly=False,string="Sale Approve")
 

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(
            due_date_check = bool(param.get_param('customer_credit_limit_app.due_date_check', False)),
            sale_approve = param.get_param('customer_credit_limit_app.sale_approve', 'before'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.due_date_check or False
        field2 = self.sale_approve or 'before'

        param.set_param('customer_credit_limit_app.due_date_check', field1)
        param.set_param('customer_credit_limit_app.sale_approve', field2)    
      
    
    
    
        

class Company_Inherit(models.Model):
	_inherit = 'res.company'

	due_date_check = fields.Boolean(string="Due Date",default=False)
	sale_approve = fields.Selection([('before','Approve Before Delivery Order'),('after','Approve After Delivery Order')],default="before",string="Sale Approve")