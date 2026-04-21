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

    @api.constrains('num_max_session_consecutive', 'max_days_in_advance')
    def _check_reservation_limits(self):
        """
        Restringir cantidad de sesiones consecutivas reservables y días de antelación de la reserva
        """
        for record in self:
            if record.num_max_session_consecutive < 0 or record.num_max_session_consecutive > 11:
                raise ValidationError(_("El número máximo de sesiones consecutivas debe estar entre 0 y 11."))
            if record.max_days_in_advance < 0 or record.max_days_in_advance > 90:
                raise ValidationError(_("Los días de antelación deben estar entre 0 y 90."))
    
    @api.onchange('bookable')
    def _onchange_bookable_update_last_reservation(self):
        """
        Calcula la última reserva del recurso cuando deja de ser reservable.
        Al estar en el mixin, funciona dinámicamente para Espacios, Empleados, etc.
        """
        for record in self:
            if not record.bookable and record._origin.id:
                
                # Usamos self._name para que funcione dinámicamente con el modelo 
                # que hereda el mixin (ej. 'maya_core.place' o 'hr.employee')
                ref_string = f'{self._name},{record._origin.id}'
                
                resource = self.env['maya_booking.booking_resource'].search([
                    ('reservable_ref', '=', ref_string)
                ], limit=1)

                if resource:
                    last_booking = self.env['maya_booking.booking'].search(
                        [('booking_resource_id', '=', resource.id)],
                        order='date_start desc',
                        limit=1
                    )
                    
                    if last_booking and last_booking.date_start:
                        record.last_reservation_date = last_booking.date_start
