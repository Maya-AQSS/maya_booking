# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BookingExample(models.Model):
    """
    Modelo de Reservas
    """
    _name = 'maya_booking.booking_example'
    _description = 'Reserva de Ejemplo'

    name = fields.Char(string="Motivo de la Reserva", required=True)
    
    resource_id = fields.Many2one(
        'maya_booking.booking_type_resource', 
        string="Recurso a Reservar", 
        required=True
    )
    
    date_start = fields.Datetime(string="Fecha Inicio", required=True, default=fields.Datetime.now)
    date_stop = fields.Datetime(string="Fecha Fin", required=True, default=fields.Datetime.now)