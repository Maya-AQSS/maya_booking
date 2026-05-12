# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

_logger = logging.getLogger(__name__)

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
                                                 help="0: Sin límite", default=2)

    max_days_in_advance = fields.Integer(string='Reserva con antelación (días)', default=15)

    # Campo de fecha de última reserva
    last_reservation_date = fields.Datetime(string=_('Última reserva')) 

    pending_bookings_count = fields.Integer(
        string=_('Reservas pendientes'), 
        readonly=True, default=0,
        help="Número de reservas futuras cuando se desactiva el recurso"
    )

    session_schedule_ids = fields.Many2many(
        "maya_core.session_schedule",
        string=_("Horarios posibles de reserva"),
    )

    display_name = fields.Char(string="Descripción", compute="_compute_display_name")

    @api.onchange('bookable')
    def _onchange_bookable_update_last_reservation(self):
        for record in self:
            real_id = record._origin.id if hasattr(record, '_origin') and record._origin else record.id

            if not record.bookable and real_id:
                resource = self.env['maya_booking.booking_resource'].search([
                    ('reservable_model', '=', self._name),
                    ('reservable_id', '=', real_id)
                ], limit=1)

                if resource:
                    # 1. Calculamos las reservas pendientes (futuras)
                    pending_count = self.env['maya_booking.booking'].search_count([
                        ('booking_resource_id', '=', resource.id),
                        ('date_stop', '>=', fields.Datetime.now())
                    ])
                    record.pending_bookings_count = pending_count

                    # 2. Buscamos la última reserva para last_reservation_date
                    last_booking = self.env['maya_booking.booking'].search(
                        [
                            ('booking_resource_id', '=', resource.id),
                            ('date_stop', '!=', False)
                        ],
                        order='date_stop desc',
                        limit=1
                    )
                    
                    if last_booking and last_booking.date_stop:
                        record.last_reservation_date = last_booking.date_stop
                    else:
                        record.last_reservation_date = False
                else:
                    record.last_reservation_date = False
                    record.pending_bookings_count = 0
            else:
                # Si se vuelve a marcar como reservable, limpiamos los campos
                record.last_reservation_date = False
                record.pending_bookings_count = 0

    # (Mantenemos el resto del código igual...)
    def write(self, vals):
        res = super().write(vals)
        if 'bookable' in vals:
            for record in self:
                resources = self.env['maya_booking.booking_resource'].sudo().search([
                    ('reservable_model', '=', self._name),
                    ('reservable_id', '=', record.id)
                ])
                if resources:
                    resources.write({'is_bookable': vals['bookable']})
        return res