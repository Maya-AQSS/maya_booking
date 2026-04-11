# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class Location(models.Model):
    _inherit = 'maya_core.location'

    def unlink(self):
        for record in self:
            espacios_anidados = self.env["maya_booking.place"].search_count([
                ("location_id", "=", record.id)
            ])
            
            if espacios_anidados > 0:
                raise UserError(
                    _("No se puede eliminar la ubicación '%s' porque tiene %s espacios de trabajo anidados.") % (record.name, espacios_anidados)
                )
                
        return super().unlink()