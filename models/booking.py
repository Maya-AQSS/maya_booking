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
    
    resource_id = fields.Many2one(
        comodel_name='maya_booking.booking_type_resource', 
        string=_("Recurso a reservar"), 
        required=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string=_("Persona que reserva"), 
        default=lambda self: self.env.user,
        readonly=True
    )

    booking_date = fields.Date(
        string=_("Fecha de Reserva"), 
        required=True, 
        default=fields.Date.context_today
    )
    
    available_schedule_ids = fields.Many2many(
        'maya_core.session_schedule',
        compute='_compute_available_schedules'
    )

    schedule_id = fields.Many2one(
        'maya_core.session_schedule', 
        string=_("Sesión de Inicio"), 
        required=True,
        domain="[('id', 'in', available_schedule_ids)]"
    )
    
    session_count = fields.Integer(string=_("Nº de Sesiones Consecutivas"), default=1, required=True)
    
    date_start = fields.Datetime(string=_("Fecha/Hora Inicio"), compute='_compute_dates', store=True)
    date_stop = fields.Datetime(string=_("Fecha/Hora Fin"), compute='_compute_dates', store=True)

    @api.depends('booking_date', 'resource_id')
    def _compute_available_schedules(self):
      """
      Busca las sesiones configuradas para ese recurso y ese día de la semana
      """
      day_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}
      for record in self:
        if record.booking_date and record.resource_id:
          place = self.env['maya_core.place'].browse(record.resource_id.reservable_id)
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
      """
      Si cambian el día o el recurso, reseteamos la sesión para evitar errores
      """
      self.schedule_id = False

    @api.depends('booking_date', 'schedule_id', 'session_count')
    def _compute_dates(self):
      """
      Calcula las horas exactas de inicio y fin basándose en el horario oficial
      """
      day_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V'}
      user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        
      for record in self:
        if not record.booking_date or not record.schedule_id:
          record.date_start = False
          record.date_stop = False
          continue
        
        # Calcular Fecha Inicio (Unimos la Fecha con la Hora del Schedule)
        start_h = int(record.schedule_id.start_time)
        start_m = int(round((record.schedule_id.start_time - start_h) * 60))
        
        dt_start_naive = datetime.combine(record.booking_date, datetime.min.time()).replace(hour=start_h, minute=start_m)
        dt_start_local = user_tz.localize(dt_start_naive)
        record.date_start = dt_start_local.astimezone(pytz.UTC).replace(tzinfo=None)
        
        # Calcular Fecha Fin sumando sesiones consecutivas
        place = self.env['maya_core.place'].browse(record.resource_id.reservable_id)
        weekday_str = day_map.get(record.booking_date.weekday())
        schedules = place.session_schedule_ids.filtered(lambda s: s.week_day == weekday_str).sorted('start_time')
        
        start_idx = schedules.ids.index(record.schedule_id.id) if record.schedule_id.id in schedules.ids else -1
        
        if start_idx != -1:
          end_idx = min(start_idx + record.session_count - 1, len(schedules) - 1)
          end_float = schedules[end_idx].end_time
          end_h = int(end_float)
          end_m = int(round((end_float - end_h) * 60))
            
          dt_end_naive = datetime.combine(record.booking_date, datetime.min.time()).replace(hour=end_h, minute=end_m)
          dt_end_local = user_tz.localize(dt_end_naive)
          record.date_stop = dt_end_local.astimezone(pytz.UTC).replace(tzinfo=None)
        else:
            record.date_stop = record.date_start + timedelta(hours=1)

    # Bloqueo de solapamientos real en BD
    @api.constrains('date_start', 'date_stop', 'resource_id')
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
          raise ValidationError(_("¡Error! Ya existe una reserva para este recurso en ese horario."))