# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPickingExtendido(models.Model):
    _inherit = "stock.picking"
    
    def write(self, vals_list):
        res = super(StockPickingExtendido, self).write(vals_list)
        self.escribir_actividad()
        return res
    
    def escribir_actividad(self):
        for pick in self:
            type_id = pick.picking_type_id
            if type_id and type_id.code == 'outgoing':
                
                vence_en_range = type_id.activity_time_range
                vence_en_date = type_id._return_selection()
                summary = type_id.activity_summary
                usuario = pick.create_uid.display_name
                tipo_act = type_id.activity_type_id.name
                creacion = pick.create_date
                creador = pick.create_uid.display_name
                vence_en = type_id.activity_date
                
                display_msg = f"""<b style='color:green;'>Vence en {vence_en_range} {vence_en_date}:</b> 
                                <b style='font-weight: bolder;'>{summary}</b> para {usuario} <br/><br/>
                                <b style='font-weight: bolder;'>Tipo de Actividad:</b> {tipo_act} <br/><br/>
                                <b style='font-weight: bolder;'>Creada:</b> {creacion} {creador} <br/><br/>
                                <b style='font-weight: bolder;'>Asignada a:</b> {creador} <br/><br/>
                                <b style='font-weight: bolder;'>Vence el: </b><b style='color:green;'>{vence_en}</b>"""
                
                pick.message_post(body=display_msg)
    

    

                
                
                
                
                   
    
  


