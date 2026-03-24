from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PlaceSessionScheduleRel(models.Model):
    _name = "maya_booking.place_session_schedule_rel"
    _description = "Horario de reserva del espacio"

    place_id = fields.Many2one("maya_booking.place", string="Espacio", required=True, ondelete="cascade")
    day_of_week = fields.Selection([
        ("0", "Lunes"),
        ("1", "Martes"),
        ("2", "Miercoles"),
        ("3", "Jueves"),
        ("4", "Viernes"),
        ("5", "Sabado"),
        ("6", "Domingo"),
    ], string="Dia", required=True)
    hour_from = fields.Float(string="Hora inicio", required=True)
    hour_to = fields.Float(string="Hora fin", required=True)


class Place(models.Model):
    _name = "maya_booking.place"
    _description = "Espacio de trabajo"

    name = fields.Char(string="Nombre", required=True, translate=True)
    location_id = fields.Many2one("maya_core.location", string="Ubicación", required=True, ondelete="restrict")

    location_name = fields.Char(related="location_id.name", string="Ubicación", store=True)

    description = fields.Text(string="Descripcion", translate=True)

    image = fields.Image(string="Imagen", max_width=1024, max_height=768)
    image_360 = fields.Image(string="Imagen 360°")
    is_panoramic = fields.Boolean(string="Es panoramica", default=False)
    floor_plan_image = fields.Image(string="Plano del espacio")

    booking_hours = fields.One2many("maya_booking.place_session_schedule_rel", "place_id", string="Horarios de reserva")

    @api.constrains("image", "image_360", "floor_plan_image")
    def _check_image_size(self):
        max_size = 5 * 1024 * 1024 
        for record in self:
            if record.image and len(record.image) > max_size:
                raise ValidationError(_("La imagen es demasiado grande."))
            if record.image_360 and len(record.image_360) > max_size:
                raise ValidationError(_("La imagen 360° es demasiado grande."))
            if record.floor_plan_image and len(record.floor_plan_image) > max_size:
                raise ValidationError(_("El plano es demasiado grande."))

    def unlink(self):
        for record in self:
            reservas = self.env["maya_booking.booking"].search_count([("place_id", "=", record.id)])
            if reservas > 0:
                raise UserError(_("No se puede eliminar el espacio '%s' porque tiene reservas asociadas.") % record.name)
        return super().unlink()