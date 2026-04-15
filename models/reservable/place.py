from odoo import models, fields, _
from odoo.exceptions import UserError

class Place(models.Model):
  _name = 'maya_core.place'
  _inherit = ['maya_core.place', 'maya_booking.reservable.mixin']
 
  def unlink(self):
    for record in self:
      reservas = self.env["maya_booking.booking"].search_count(
        [("place_id", "=", record.id)]
      )
      if reservas > 0:
        raise UserError(
            _("No se puede eliminar el espacio '%s' porque tiene reservas asociadas.") % record.name
        )
      
    return super().unlink()