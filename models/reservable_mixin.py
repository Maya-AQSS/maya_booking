# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ReservableMixin(models.AbstractModel):
    _name = 'maya_booking.reservable.mixin'
    _description = 'Mixin reservables'

    bookable = fields.Boolean(default=True, string='Es reservable')
    
    resource_type = fields.Selection([
        ('E', 'Empleado'),
        ('S', 'Espacio'),
        ('W', 'Puesto'),
        ('I', 'Elemento de inventario'),
    ], string='Tipo de recurso', default='S')
    
    num_max_session_consecutive = fields.Integer(string='Número máximo de sesiones consecutivas', 
                                                 help="Número máximo de sesiones consecutivas que se pueden reservar. 0: Sin límite (hasta final del día)",
                                               default=2)

    max_days_in_advance = fields.Integer(string='Reserva con antelación (días)', 
                                         help="Máximos días de antelación con los que se puede realizar una reserva. 0: sin límite", default=15)

    # cada vez que se añada una reserva debe actualizarse
    # es útil para gestionar las reservas en caso de que el recurso pase a ser no reservable
    last_reservation_date = fields.Datetime(string=_('Última reserva')) 

    session_schedule_ids = fields.Many2many(
        "maya_core.session_schedule",
        string=_("Horarios posibles de reserva"),
        help=_("Consultar las reservas para ver la disponibilidad"),
    )

    display_name = fields.Char(string="Descripción", compute="_compute_display_name")
