# -*- coding: utf-8 -*-

from . import controllers
from . import models

def contact_type_restrictions_uninstall_hook(cr, registry):
    cr.execute("INSERT INTO rule_group_rel VALUES (10, 1)")
    cr.commit()
    cr.execute("UPDATE ir_rule SET global = FALSE WHERE id = 10")
    cr.commit()