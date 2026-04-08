# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class BookingExample(models.Model):
    _name = 'maya_booking.booking_example'
    _description = _('Reserva y Slots Disponibles')

    name = fields.Char(
        string=_("Motivo de la Reserva"), 
        default="Disponible",
        help=_("Indica el motivo o razón de la reserva.")
    )
    resource_id = fields.Many2one(
        comodel_name='maya_booking.booking_type_resource', 
        string=_("Recurso"), 
        required=True,
        help=_("Recurso físico que se va a reservar.")
    )
    date_start = fields.Datetime(
        string=_("Fecha Inicio"), 
        required=True
    )
    date_stop = fields.Datetime(
        string=_("Fecha Fin"), 
        required=True
    )
    state = fields.Selection(
        selection=[
            ('available', _('Disponible')),
            ('booked', _('Reservado'))
        ], 
        string=_("Estado"), 
        default='available', 
        required=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string=_("Persona que reserva"),
        help=_("Usuario que ha confirmado la reserva.")
    )

    available_slot_domain_ids = fields.Many2many(
        comodel_name='maya_booking.booking_example',
        compute='_compute_available_domain_slots',
        string=_("Dominio de Sesiones Disponibles")
    )
    
    additional_slot_ids = fields.Many2many(
        comodel_name='maya_booking.booking_example',
        relation='booking_additional_slots_rel', 
        column1='booking_id',
        column2='additional_id',
        string=_("Añadir otras sesiones"),
        help=_("Permite reservar múltiples sesiones disponibles en la misma acción.")
    )

    is_past = fields.Boolean(
        string=_("Es Pasado"),
        compute='_compute_is_past',
        help=_("Indica si la sesión ya ha comenzado o finalizado.")
    )
    
    timeline_state = fields.Selection(
        selection=[
            ('available', _('Disponible')),
            ('booked', _('Reservado')),
            ('past_available', _('Pasado (Libre)')),
            ('past_booked', _('Pasado (Reservado)'))
        ],
        compute='_compute_timeline_state',
        string=_("Estado para Timeline")
    )

    @api.depends('state', 'is_past')
    def _compute_timeline_state(self):
        """Unifica el estado y el tiempo para que la vista no tenga que pensar"""
        for record in self:
            if record.is_past:
                if record.state == 'booked':
                    record.timeline_state = 'past_booked'
                else:
                    record.timeline_state = 'past_available'
            else:
                record.timeline_state = record.state

    @api.depends('date_start')
    def _compute_is_past(self):
        """Calcula en tiempo real si el slot ya se ha quedado atrás"""
        now = fields.Datetime.now()
        for record in self:
            record.is_past = bool(record.date_start and record.date_start < now)

    def _compute_display_name(self):
        """
        Sobrescribe el nombre a mostrar en los registros para que las casillas 
        de selección múltiple muestren la fecha y hora de forma amigable, 
        adaptada a la zona horaria local del usuario.
        """
        for record in self:
            if record.state == 'available' and record.date_start and record.date_stop:
                # Convertimos de UTC a la hora local del usuario
                start_local = fields.Datetime.context_timestamp(self, record.date_start)
                stop_local = fields.Datetime.context_timestamp(self, record.date_stop)
                
                # Formato deseado: 13/04/2026 14:00 - 15:00
                record.display_name = f"{start_local.strftime('%d/%m/%Y %H:%M')} - {stop_local.strftime('%H:%M')}"
            else:
                record.display_name = record.name or _('Nuevo')

    @api.depends('resource_id', 'date_start')
    def _compute_available_domain_slots(self):
        """
        Calcula qué otros slots están disponibles para el mismo recurso, 
        durante la misma semana, y que se encuentren en el futuro.
        """
        now = fields.Datetime.now()
        
        for record in self:
            if not record.date_start or not record.resource_id:
                record.available_slot_domain_ids = False
                continue
                
            # Calcular inicio y fin de la semana actual del slot
            start_of_week = record.date_start - timedelta(days=record.date_start.weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0)
            end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

            # Buscar desde el momento actual o el inicio de la semana (evita slots pasados)
            search_start = max(now, start_of_week)

            # Extraer el ID real si estamos interactuando en un formulario no guardado (NewId)
            current_id = record._origin.id if record._origin else record.id

            available_slots = self.env['maya_booking.booking_example'].search([
                ('resource_id', '=', record.resource_id.id),
                ('state', '=', 'available'),
                ('date_start', '>=', search_start),
                ('date_stop', '<=', end_of_week),
                ('id', '!=', current_id)
            ])
            record.available_slot_domain_ids = available_slots

    def action_book_slot(self):
        """
        Confirma la reserva del slot actual y de los slots adicionales 
        seleccionados en el formulario de forma concurrente.
        """
        for record in self:
            if record.is_past:
                raise ValidationError(_("No puedes realizar ni modificar reservas de sesiones que ya han pasado."))
            motivo = record.name
            
            # Validación del motivo escrito por el usuario
            if motivo in ('Disponible', 'Available') or not motivo:
                raise ValidationError(_("Por favor, introduce un motivo real para la reserva en lugar de 'Disponible'."))

            # 1. Marcar el registro actual como reservado
            record.write({
                'state': 'booked',
                'name': motivo,
                'user_id': self.env.user.id
            })

            # 2. Procesar los slots adicionales seleccionados
            slots_adicionales = record.additional_slot_ids.filtered(lambda s: s.state == 'available')
            if slots_adicionales:
                slots_adicionales.write({
                    'state': 'booked',
                    'name': motivo,
                    'user_id': self.env.user.id
                })

        # Forzar el cierre de la ventana modal para refrescar la vista subyacente (Timeline)
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel_booking(self):
        """
        Libera un slot reservado, devolviéndolo a su estado original de disponibilidad.
        """
        for record in self:
            record.write({
                'state': 'available',
                'name': 'Disponible',
                'user_id': False
            })

    @api.model
    def _cron_generate_slots(self, days_ahead=14):
        """
        Genera físicamente en la base de datos los registros de 'slots disponibles'
        basándose en los horarios configurados para cada recurso.
        Se ejecuta periódicamente mediante una acción planificada (ir.cron).
        
        :param days_ahead: Número de días hacia el futuro a procesar.
        """
        # Mapeo estándar de días de Python (0=Lunes) a la nomenclatura del sistema
        day_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}
        
        places = self.env['maya_booking.place'].search([])
        resources = self.env['maya_booking.booking_type_resource'].search([
            ('reservable_model', '=', 'maya_booking.place'),
            ('reservable_id', 'in', places.ids)
        ])

        today = fields.Datetime.now().replace(hour=0, minute=0, second=0)

        for resource in resources:
            place = places.filtered(lambda p: p.id == resource.reservable_id)
            if not place or not place.session_schedule_ids:
                continue

            for i in range(days_ahead):
                current_day = today + timedelta(days=i)
                weekday_str = day_map.get(current_day.weekday())

                if weekday_str:
                    sessions = place.session_schedule_ids.filtered(lambda s: s.week_day == weekday_str)
                    
                    for session in sessions:
                        # Conversión de hora decimal (Odoo) a horas y minutos enteros
                        start_h = int(session.start_time)
                        start_m = int((session.start_time - start_h) * 60)
                        end_h = int(session.end_time)
                        end_m = int((session.end_time - end_h) * 60)

                        slot_start = current_day.replace(hour=start_h, minute=start_m)
                        slot_end = current_day.replace(hour=end_h, minute=end_m)

                        # Evitar la duplicación de slots ya existentes
                        existing_slot = self.search([
                            ('resource_id', '=', resource.id),
                            ('date_start', '=', slot_start),
                            ('date_stop', '=', slot_end)
                        ], limit=1)

                        if not existing_slot:
                            self.create({
                                'name': 'Disponible',
                                'resource_id': resource.id,
                                'date_start': slot_start,
                                'date_stop': slot_end,
                                'state': 'available'
                            })