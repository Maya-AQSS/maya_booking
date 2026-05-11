# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class ReservableMixin(models.AbstractModel):
    _name = 'maya_booking.reservable.mixin'
    _description = 'Mixin reservables'

    # 1. CAMBIO: Por defecto, los recursos nacen sin ser reservables
    bookable = fields.Boolean(default=False, string='Es reservable')
    
    resource_type = fields.Selection([
        ('E', 'Empleado'),
        ('S', 'Espacio'),
        ('W', 'Puesto'),
        ('I', 'Elemento de inventario'),
    ], string='Tipo de recurso', default='S')
    
    num_max_session_consecutive = fields.Integer(string='Número máximo de sesiones consecutivas', 
                                                 help="0: Sin límite", default=2)

    max_days_in_advance = fields.Integer(string='Reserva con antelación (días)', default=15)

    last_reservation_date = fields.Datetime(string=_('Última reserva')) 

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
            else:
                record.last_reservation_date = False


    # --- NUEVA LÓGICA DE CREACIÓN AUTOMÁTICA ---

    def _ensure_booking_resource(self):
        """
        Método auxiliar para comprobar si existe el booking_resource 
        y crearlo si el recurso es bookable.
        """
        for record in self:
            if record.bookable:
                # Buscamos si ya existe el recurso en la tabla de reservas
                resource_exists = self.env['maya_booking.booking_resource'].sudo().search_count([
                    ('reservable_model', '=', self._name),
                    ('reservable_id', '=', record.id)
                ])
                
                # Si no existe, lo creamos
                if not resource_exists:
                    self.env['maya_booking.booking_resource'].sudo().create({
                        'reservable_model': self._name,
                        'reservable_id': record.id,
                        # El reference se computa solo gracias al _compute_reservable_ref en booking_resource
                    })

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobreescribimos create por si el registro se crea ya con bookable=True
        """
        records = super().create(vals_list)
        # Llamamos al método auxiliar para crear el recurso si es necesario
        records._ensure_booking_resource()
        return records

    def write(self, vals):
        """
        Ampliamos el write que tenías para gestionar la creación automática
        """
        res = super().write(vals)
        
        if 'bookable' in vals:
            for record in self:
                # 1. Propagamos el valor al is_bookable (como ya hacías)
                resources = self.env['maya_booking.booking_resource'].sudo().search([
                    ('reservable_model', '=', self._name),
                    ('reservable_id', '=', record.id)
                ])
                if resources:
                    resources.write({'is_bookable': vals['bookable']})
                
                # 2. Si acaba de pasar a True y no existía el registro, lo creamos
                if vals['bookable']:
                    record._ensure_booking_resource()
                    
        return res