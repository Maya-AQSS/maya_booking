from odoo import fields, models, _


class ReservableMixin(models.AbstractModel):
    _name = 'maya_booking.reservable.mixin'
    _description = 'Mixin para cualquier recurso reservable'

    bookable = fields.Boolean(default=True, string=_('Es reservable'))

    # booking_ids = fields.One2many('maya_booking.booking', 'bookable_ref', string="Reservas")

    # Aplicable como herencia, crear trozos de los modelos como places 