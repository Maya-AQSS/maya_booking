from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class Place(models.Model):
    _name = "maya_booking.place"
    _description = "Espacio de trabajo"

    name = fields.Char(string=_("Nombre"), required=True)
    location_id = fields.Many2one(
        "maya_core.location",
        string=_("Ubicación"),
        required=True,
        ondelete="restrict",
    )
    location_name = fields.Char(related="location_id.name", string=_("Nombre de ubicación"))
    description = fields.Text(string=_("Descripción"))

    image = fields.Image(
        string=_("Imagen principal"),
        max_width=1024,
        max_height=768,
        attachment=True,
    )
    image_360 = fields.Image(
        string=_("Imagen 360°"),
        attachment=True,
    )
    is_panoramic = fields.Boolean(string=_("Es panorámica"), default=False)
    floor_plan_image = fields.Image(
        string=_("Plano del espacio"),
        attachment=True,
    )

    session_schedule_ids = fields.Many2many(
        "maya_core.session_schedule",
        string=_("Horarios de reserva"),
    )

    @api.constrains("image", "image_360", "floor_plan_image")
    def _check_image_size(self):
        max_size = 10 * 1024 * 1024
        for record in self:
            if record.image and len(record.image) > max_size:
                raise ValidationError(_("La imagen principal es demasiado grande. Máximo 10 MB."))
            if record.image_360 and len(record.image_360) > max_size:
                raise ValidationError(_("La imagen 360° es demasiado grande. Máximo 10 MB."))
            if record.floor_plan_image and len(record.floor_plan_image) > max_size:
                raise ValidationError(_("El plano es demasiado grande. Máximo 10 MB."))

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