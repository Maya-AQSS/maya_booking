# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz

class Booking(models.Model):
    """
    Reservas
    """
    _name = 'maya_booking.booking'
    _description = _('Reservas')

    name = fields.Char(string=_("Motivo / Descripción"))

    reason =  fields.Selection(
       [('TC', _('Tutoria colectiva')),     
        ('TI', _('Tutoria individual')),    
        ('R', _('Reunión')),     
        ('EX', _('Examen')),
        ('O', _('Otros')) ],
        string=_("Motivo"),  
        default='TI', required=True) 
    
    description =  fields.Text(_('Descripción'), 
                               help=_('Asignatura y estudios, descripción detallada de la reunión, etc.'))
    
    booking_resource_id = fields.Many2one(
        comodel_name='maya_booking.booking_resource', 
        string=_("Recurso a reservar"), 
        required=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string=_("Usuario"), 
        help=_("Usuario que reserva"), 
        default=lambda self: self.env.user,
        readonly=True
    )

    booking_date = fields.Date(
        string=_("Fecha"), 
        help=_("Fecha de la reserva"),
        required=True, 
        default=fields.Date.context_today
    )

    session_ids = fields.Many2many(
        'maya_core.session_schedule',
        'maya_booking_session_rel',
        'booking_id',
        'session_id',
        string=_("Sesiones"),
        help=_("Seleccione las sesiones consecutivas para su reserva.")
    )

    date_start = fields.Datetime(string=_("Inicio"), compute='_compute_dates', store=True)
    date_stop = fields.Datetime(string=_("Fin"), compute='_compute_dates', store=True) 

    resource_name = fields.Char(_('Recurso'), related="booking_resource_id.resource_name")

    @api.onchange('booking_date', 'booking_resource_id', 'session_ids')
    def _onchange_filter_sessions(self):
      """
      Filtra sesiones por:
      1. Día de la semana y ubicación.
      2. Disponibilidad (que no estén ya reservadas por otros).
      3. Continuidad (solo mostrar la siguiente a la última elegida).
      """
      if not self.booking_date or not self.booking_resource_id:
        return {'domain': {'session_ids': [('id', '=', 0)]}}

      # 1. Filtro básico: Día y Ubicación
      weekday_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V'}
      day_code = weekday_map.get(self.booking_date.weekday())
      
      if not day_code:
        return {'domain': {'session_ids': [('id', '=', 0)]}}

      location_id = self.booking_resource_id.reservable_ref.location_id.id
      
      # Base del dominio
      domain = [
          ('week_day', '=', day_code),
          ('location_id', '=', location_id),
          ('active', '=', True)
      ]

      # 2. Excluir sesiones ya reservadas por otros en esa fecha
      # Buscamos reservas confirmadas para este recurso y fecha
      existing_bookings = self.env['maya_booking.booking'].search([
          ('booking_date', '=', self.booking_date),
          ('booking_resource_id', '=', self.booking_resource_id.id),
          ('id', '!=', self._origin.id if self._origin else False) # Ignorar la reserva actual
      ])
      
      booked_session_ids = existing_bookings.mapped('session_ids').ids
      if booked_session_ids:
          domain.append(('id', 'not in', booked_session_ids))

      # 3. Lógica de "Posteriores y Consecutivas"
      if self.session_ids:
          # Obtenemos la hora de fin de la sesión más tardía seleccionada
          last_end_time = max(self.session_ids.mapped('end_time'))
          
          # Filtramos para que SOLO aparezca la sesión que empieza justo donde acaba la anterior
          # Esto obliga a que la selección sea perfectamente encadenada
          domain.append(('start_time', '=', last_end_time))
      
      return {'domain': {'session_ids': domain}}

    @api.depends('booking_date', 'session_ids.start_time', 'session_ids.end_time')
    def _compute_dates(self):
      """
      Calcula el inicio de la primera sesión y el fin de la última
      combinándolos con la fecha de la reserva.
      """
      for record in self:
        if record.booking_date and record.session_ids:
          # 1. Obtener los extremos de las sesiones seleccionadas
          # Usamos min y max sobre el conjunto de sesiones vinculadas
          start_hour = min(record.session_ids.mapped('start_time'))
          end_hour = max(record.session_ids.mapped('end_time'))

          # 2. Helper para convertir Float (9.5) a Datetime
          record.date_start = self._combine_date_and_float(record.booking_date, start_hour)
          record.date_stop = self._combine_date_and_float(record.booking_date, end_hour)
        else:
          record.date_start = False
          record.date_stop = False

    def _combine_date_and_float(self, base_date, float_time):
      """
      Convierte una fecha y una hora float en un objeto Datetime.
      Ejemplo: 2026-04-17 + 9.5 -> 2026-04-17 09:30:00
      """
      # Extraer horas y minutos del float (ej: 9.75 -> 9 horas, 0.75 * 60 = 45 min)
      hours = int(float_time)
      minutes = int(round((float_time - hours) * 60))
      
      # Combinar con la fecha base
      return datetime.combine(base_date, datetime.min.time()).replace(
          hour=hours, minute=minutes
      )
    
    @api.model
    def get_sessions_for_slot(self, resource_id, date_str, start_float, end_float):
      """
      Dado un recurso, fecha y rango horario (floats),
      devuelve las sesiones que cubren ese rango.
      Usado desde el timeline JS para pre-rellenar el formulario.
      """
      from datetime import date as date_type

      # Convertir fecha string a date
      booking_date = fields.Date.from_string(date_str)

      # Día de la semana
      weekday_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V'}
      day_code = weekday_map.get(booking_date.weekday())
      if not day_code:
          return []

      # Obtener location del recurso
      resource = self.env['maya_booking.booking_resource'].browse(resource_id)
      if not resource or not resource.reservable_ref:
          return []

      location_id = resource.reservable_ref.location_id.id

      # Buscar sesiones que solapen con el rango seleccionado
      sessions = self.env['maya_core.session_schedule'].search([
          ('week_day', '=', day_code),
          ('location_id', '=', location_id),
          ('active', '=', True),
          ('start_time', '<', end_float),    # empieza antes del fin del slot
          ('end_time', '>', start_float),    # termina después del inicio del slot
      ], order='start_time asc')

      return sessions.ids