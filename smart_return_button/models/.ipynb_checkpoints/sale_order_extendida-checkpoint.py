# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrderExtendida(models.Model):
    _inherit = "sale.order"

    returns_count = fields.Integer(string='Cantidad de Devoluciones', compute='_compute_returns')
    invoice_min = fields.Boolean(string="¿Existe al menos una devolución o un despacho?", compute='_get_move_type')

    @api.depends('picking_ids')
    def _compute_returns(self):
        for order in self:
            order.returns_count = 0
            for pick in order.picking_ids:
                if (pick.picking_type_code == 'incoming' and pick.location_id.usage == 'customer') or\
                   (pick.picking_type_code == 'outgoing' and pick.state == 'done'):
                    order.returns_count+=1

            
    def _get_action_view_returns(self, pickings):

        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id

        picking_id = pickings[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id,
                                 default_picking_type_id=picking_id.picking_type_id.id, 
                                 default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action            

        
        
    def action_view_return(self):

        sale_picks = self.picking_ids.filtered(lambda o: (o.picking_type_code == 'incoming' and o.location_id.usage == 'customer') or (o.picking_type_code == 'outgoing' and o.state == 'done'))
        
        return self._get_action_view_returns(sale_picks)

    @api.depends('invoice_ids')
    def _get_move_type(self):
        min = [id for id in self.invoice_ids if id.move_type == 'out_invoice']
        self.invoice_min = True if min else False
