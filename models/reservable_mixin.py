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

    session_schedule_ids = fields.Many2many(
        "maya_core.session_schedule",
        string=_("Horarios posibles de reserva"),
    )

    display_name = fields.Char(string="Descripción", compute="_compute_display_name")

    @api.onchange('bookable')
    def _onchange_bookable_update_last_reservation(self):
        for record in self:
            _logger.info("\n" + "DEBUG " * 10)
            _logger.info(f">>> ONCHANGE BOOKABLE EJECUTADO PARA: {record}")
            _logger.info(f">>> VALOR DE BOOKABLE: {record.bookable}")

            # Intentamos obtener el ID real (del _origin si estamos en edición)
            real_id = record._origin.id if hasattr(record, '_origin') and record._origin else record.id
            _logger.info(f">>> ID DETECTADO (Real/Origin): {real_id}")

            if not record.bookable and real_id:
                # IMPORTANTE: Buscar por modelo e ID es más seguro que por el string 'reservable_ref'
                _logger.info(f">>> BUSCANDO booking_resource PARA {self._name} con ID {real_id}")
                
                resource = self.env['maya_booking.booking_resource'].search([
                    ('reservable_model', '=', self._name),
                    ('reservable_id', '=', real_id)
                ], limit=1)

                if resource:
                    _logger.info(f">>> RECURSO ENCONTRADO: {resource.id} - {resource.resource_name}")
                    
                    # Buscamos la última reserva
                    last_booking = self.env['maya_booking.booking'].search(
                        [
                            ('booking_resource_id', '=', resource.id),
                            ('date_stop', '!=', False)  # Ignorar reservas rotas
                        ],
                        order='date_stop desc',
                        limit=1
                    )
                    
                    if last_booking:
                        _logger.info(f">>> RESERVA ENCONTRADA: ID {last_booking.id}, Motivo: {last_booking.name}")
                        _logger.info(f">>> VALOR DE date_stop EN RESERVA: {last_booking.date_stop}")
                        
                        if last_booking.date_stop:
                            record.last_reservation_date = last_booking.date_stop
                            _logger.info(f">>> ÉXITO: Asignada fecha {last_booking.date_stop} al campo.")
                        else:
                            _logger.info(">>> ERROR: La reserva existe pero date_stop está VACÍO.")
                            record.last_reservation_date = False
                    else:
                        _logger.info(">>> AVISO: El recurso existe pero no tiene ninguna reserva vinculada.")
                        record.last_reservation_date = False
                else:
                    _logger.info(f">>> ERROR: No se ha encontrado ningún booking_resource que apunte a {self._name} con ID {real_id}")
                    record.last_reservation_date = False
            
            else:
                _logger.info(">>> LIMPIEZA: Bookable es True o no hay ID real. Limpiando fecha.")
                record.last_reservation_date = False
            
            _logger.info("DEBUG " * 10 + "\n")

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