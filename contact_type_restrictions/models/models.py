# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import lazy_property

USER_PRIVATE_FIELDS = []

class Users(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        list_groups = [
            'Visualizar Proveedores', 
            'Visualizar Proveedores Nacionales', 
            'Visualizar Clientes', 
            'Gestionar Proveedores',
            'Gestionar Clientes'
        ]
        print('vals_list---->', vals_list)
        for val in set(map(lambda i: f"in_group_{i}", self.env['res.groups'].search([('name', 'in', list_groups)]).ids)).intersection(set(vals_list[0])):
            if vals_list[0].get(val) == True:
                vals_list[0].update({
                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Usuario Interno 2')]).ids[0]): False,
                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Creación de contactos')]).ids[0]): False
                })

        if vals_list:
            vals_list[0].update({
                f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Usuario Interno 2')]).ids[0]): True
            })
        

        users = super(Users, self).create(vals_list)
        for user in users:
            # if partner is global we keep it that way
            if user.partner_id.company_id:
                user.partner_id.company_id = user.company_id
            user.partner_id.active = user.active
        return users

    def write(self, values):
        if values.get('active') and SUPERUSER_ID in self._ids:
            raise UserError(_("You cannot activate the superuser."))
        if values.get('active') == False and self._uid in self._ids:
            raise UserError(_("You cannot deactivate the user you're currently logged in as."))

        if values.get('active'):
            for user in self:
                if not user.active and not user.partner_id.active:
                    user.partner_id.toggle_active()
        if self == self.env.user:
            writeable = self.SELF_WRITEABLE_FIELDS
            for key in list(values):
                if not (key in writeable or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if values['company_id'] not in self.env.user.company_ids.ids:
                        del values['company_id']
                # safe fields only, so we write as super-user to bypass access rights
                self = self.sudo().with_context(binary_field_real_user=self.env.user)

        list_groups = [
            'Visualizar Proveedores', 
            'Visualizar Proveedores Nacionales', 
            'Visualizar Clientes', 
            'Gestionar Proveedores',
            'Gestionar Clientes'
        ]
        for val in set(map(lambda i: f"in_group_{i}", self.env['res.groups'].search([('name', 'in', list_groups)]).ids)).intersection(values):
            if values.get(val) == True:
                values.update({
                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Usuario Interno 2')]).ids[0]): False,
                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Creación de contactos')]).ids[0]): False
                })

        print('si esta pasando por aqui o no?')
        print(self, values)
        res = super(Users, self).write(values)
        if 'company_id' in values:
            for user in self:
                # if partner is global we keep it that way
                if user.partner_id.company_id and user.partner_id.company_id.id != values['company_id']:
                    user.partner_id.write({'company_id': user.company_id.id})

        if 'company_id' in values or 'company_ids' in values:
            # Reset lazy properties `company` & `companies` on all envs
            # This is unlikely in a business code to change the company of a user and then do business stuff
            # but in case it happens this is handled.
            # e.g. `account_test_savepoint.py` `setup_company_data`, triggered by `test_account_invoice_report.py`
            for env in list(self.env.transaction.envs):
                if env.user in self:
                    lazy_property.reset_all(env)

        # clear caches linked to the users
        if self.ids and 'groups_id' in values:
            # DLE P139: Calling invalidate_cache on a new, well you lost everything as you wont be able to take it back from the cache
            # `test_00_equipment_multicompany_user`
            self.env['ir.model.access'].call_cache_clearing_methods()

        # per-method / per-model caches have been removed so the various
        # clear_cache/clear_caches methods pretty much just end up calling
        # Registry._clear_cache
        invalidation_fields = {
            'groups_id', 'active', 'lang', 'tz', 'company_id',
            *USER_PRIVATE_FIELDS,
            *self._get_session_token_fields()
        }
        if (invalidation_fields & values.keys()) or any(key.startswith('context_') for key in values):
            self.clear_caches()

        return res

class Groups(models.Model):
    _inherit = 'res.groups'

    @api.model_create_multi
    def create(self, vals_list):
        print('aja', self, vals_list)
        if vals_list:
            if 'name' in vals_list[0] and vals_list[0].get('name') == 'Usuario Interno 2':
                vals_list[0].update({
                    'users': [(4, usuario.id) for usuario in self.env['res.users'].search([])]
                })
                print('al fin puedo hacer algo con esto')
        return super(Groups, self).create(vals_list)

    def write(self, vals):
        list_groups = [
            'Visualizar Proveedores', 
            'Visualizar Proveedores Nacionales', 
            'Visualizar Clientes', 
            'Gestionar Proveedores',
            'Gestionar Clientes'
        ]
        if self.id in self.env['res.groups'].search([('name', 'in', list_groups)]).ids:
            print('se esta modificando un grupo mio')
            if 'name' not in vals or 'comment' not in vals or 'category_id' not in vals:
                print('y justamente no es porque se creó')
                if self.users.ids is not None and vals.get('users') is not None:
                    if len(self.users.ids) < len(vals.get('users')[0][2]):
                        print('es una añadicion')
                        print('pendiente con una vaina menor')
                        usuario = vals.get('users')[0][2][-1]
                        values = {}
                        print('usuario', usuario)
                        values.update({
                            f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Usuario Interno 2')]).ids[0]): False,
                            f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Creación de contactos')]).ids[0]): False
                        })
                        super(Users, self.env['res.users'].search([('id', '=', usuario)])).write(values)
                    else:
                        print('es una eleminiacion')

        if 'name' in vals and vals.get('name') == 'Usuario Interno 2':
            print('se esta creando usuario interno 2')
            if vals.get('users'):
                print('y si hay usuarios dentro de usuario interno 2')
                for usuario2 in self.users.ids:
                    print(usuario2, self.env['res.groups'].search([('name', 'in', list_groups)]).mapped('users').ids)
                    if usuario2 in self.env['res.groups'].search([('name', 'in', list_groups)]).mapped('users').ids:
                        print('efectivamente si esta dentro de mis grupos. A sacarlo de usuario interno 2')

                        for valores in vals.get('users'):
                            if valores[-1] == usuario2:
                                vals.get('users').remove(valores)

                                values = {}
                                values.update({
                                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Usuario Interno 2')]).ids[0]): False,
                                    f"in_group_" + str(self.env['res.groups'].search([('name', '=', 'Creación de contactos')]).ids[0]): False
                                })
                                
                                # super(Users, self2).write(values)
                                self.env['res.users'].search([('id', '=', usuario2)]).write(values)

        if 'name' in vals:
            if vals['name'].startswith('-'):
                raise UserError(_('The name of the group can not start with "-"'))
        # invalidate caches before updating groups, since the recomputation of
        # field 'share' depends on method has_group()
        # DLE P139
        if self.ids:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['res.users'].has_group.clear_cache(self.env['res.users'])
        print('self------>', self, 'vals------>', vals, 'self.users', self.users.ids, len(self.users.ids))
        
        return super(Groups, self).write(vals)


class Partner(models.Model):
    _inherit = 'res.partner'

    proveedor_internat = fields.Boolean(
        string='¿Es Internacional?',
        default=False
    )

