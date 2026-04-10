from odoo import fields, models, _


class Resource(models.Model):
    _name = 'maya_booking.resource'
    _description = 'Recurso reservable'

    model_name = fields.Char(string=_('Modelo'), required=True)

    res_id = fields.Integer(string=_('ID original'), required=True)

    name = fields.Char(string=_('Nombre'), required=True)

    active = fields.Boolean(string=_('Activo'), default=True)

    booking_limit_date = fields.Date(string=_('Fecha límite de reserva'))
