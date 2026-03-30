# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingTypeResource(models.Model):
    """
    Interfaz polimórfico con varios tipos de recursos
    """

    _name = 'maya_booking.booking_type_resource'
    _description = 'Recursos Reservables'

    type_id = fields.Many2one('maya_booking.booking_type', ondelete='cascade') 
    reservable_model = fields.Char(required=True)      # ej: 'maya_core.employee', 
    reservable_id = fields.Integer(required=True)   # el id del registro al que queremos apuntar
    # reservable_ref = fields.Reference( selection='_get_reservable_models',     compute='_compute_reservable_ref',     store=True )