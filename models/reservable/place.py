from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Place(models.Model):
  _name = 'maya_core.place'
  _inherit = ['maya_core.place', 'maya_booking.reservable.mixin']


  @api.depends('name', 'location_id')
  def _compute_display_name(self):
    for record in self:
      if record:
        record.display_name = record.name + " - [" + record.location_id.name + "]"
      else:
        record.display_name = _("Sin recurso")


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