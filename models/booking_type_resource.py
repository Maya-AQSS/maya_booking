# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingTypeResource(models.Model):
    """
    Interfaz polimórfico con varios tipos de recursos
    """

    _name = 'maya_booking.booking_type_resource'
    _description = 'Recursos Reservables'

    name = fields.Char(string="Nombre del Recurso", required=True)

    type_id = fields.Many2one('maya_booking.booking_type', ondelete='cascade') 
    reservable_model = fields.Char()      # ej: 'maya_core.employee', 
    reservable_id = fields.Integer()   # el id del registro al que queremos apuntar
    
    reservable_ref = fields.Reference(
        selection='_get_reservable_models', 
        string="Recurso Físico/Real",
        compute='_compute_reservable_ref', 
        inverse='_inverse_reservable_ref', 
        store=True,
        required=True 
    )

    @api.model
    def _get_reservable_models(self):
        """
        Lista de modelos reales que pueden ser un recurso
        """
        return [
            ('res.users', 'Usuario (Prueba)'),
            ('res.partner', 'Contacto/Empresa (Prueba)'),
            ('maya_core.employee', 'Empleado'), 
        ]

    @api.depends('reservable_model', 'reservable_id')
    def _compute_reservable_ref(self):
        """
        construye el Reference para la vista
        """
        for rec in self:
            if rec.reservable_model and rec.reservable_id:
                rec.reservable_ref = f"{rec.reservable_model},{rec.reservable_id}"
            else:
                rec.reservable_ref = False

    def _inverse_reservable_ref(self):
        """
       guarda el modelo y el ID del recurso que el usuario elija en la BD
        """
        for rec in self:
            if rec.reservable_ref:
                rec.reservable_model = rec.reservable_ref._name
                rec.reservable_id = rec.reservable_ref.id
            else:
                rec.reservable_model = False
                rec.reservable_id = 0