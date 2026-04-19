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

    name = fields.Char(string=_("Motivo / Descripción"), required=True)
    
    booking_resource_id = fields.Many2one(
        comodel_name='maya_booking.booking_resource', 
        string=_("Recurso a reservar"), 
        required=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string=_("Usuario que reserva"), 
        default=lambda self: self.env.user,
        readonly=True
    )

    booking_date = fields.Date(
        string=_("Fecha de la reserva"), 
        required=True, 
        default=fields.Date.context_today
    )
    
    """   available_schedule_ids = fields.Many2many(
        'maya_core.session_schedule',
        compute='_compute_available_schedules'
    ) """

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
    
    """ schedule_ids = fields.Many2many(
        'maya_core.session_schedule', 
        string=_("Sesiones"), 
        required=True,
        domain="[('id', 'in', available_schedule_ids)]"
    ) """
    
    """ session_count = fields.Integer(string=_("Nº de Sesiones Consecutivas"), default=1, required=True)
    
    date_start = fields.Datetime(string=_("Fecha y hora inicio"), compute='_compute_dates', store=True)
    date_stop = fields.Datetime(string=_("Fecha y hora fin"), compute='_compute_dates', store=True) """

    """
    @api.depends('booking_date', 'booking_resource_id')
    def _compute_available_schedules(self):
    
      Busca las sesiones configuradas para ese recurso y ese día de la semana
    

      day_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V'}
      for record in self:
        if record.booking_date and record.booking_resource_id:
          place = self.env['maya_core.place'].browse(record.booking_resource_id.reservable_id)
          weekday_str = day_map.get(record.booking_date.weekday())
                
          if weekday_str:
            schedules = place.session_schedule_ids.filtered(lambda s: s.week_day == weekday_str)
            record.available_schedule_ids = schedules
          else:
            record.available_schedule_ids = False
        else:
            record.available_schedule_ids = False

    @api.onchange('booking_date', 'resource_id')
    def _onchange_clear_schedule(self):
      
      Si cambian el día o el recurso, reseteamos la sesión para evitar errores
      
      self.schedule_id = False

     """

    # Bloqueo de solapamientos real en BD
    """  @api.constrains('date_start', 'date_stop', 'resource_id')
    def _check_overlap(self):
      for record in self:
        if not record.date_start or not record.date_stop:
          continue
        
        domain = [
            ('id', '!=', record.id),
            ('resource_id', '=', record.resource_id.id),
            ('date_start', '<', record.date_stop),
            ('date_stop', '>', record.date_start)
        ]
        if self.search_count(domain) > 0:
          raise ValidationError(_("¡Error! Ya existe una reserva para este recurso en ese horario.")) """