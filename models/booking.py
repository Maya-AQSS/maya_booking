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

    name = fields.Char(string=_("Descripción"), compute='_compute_name', store=True)

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
        required=True,
        domain="[('is_bookable', '=', True)]" # Oculta recursos no reservables del desplegable
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
        string=_("Sesiones reservadas"),
        help=_("Seleccione las sesiones consecutivas para su reserva.")
    )

    date_start = fields.Datetime(string=_("Inicio"), compute='_compute_dates', store=True)
    date_stop = fields.Datetime(string=_("Fin"), compute='_compute_dates', store=True) 

    resource_name = fields.Char(_('Recurso'), related="booking_resource_id.resource_name")

    # la usamos para filtrar datos en la vista
    available_session_ids = fields.Many2many(
      'maya_core.session_schedule',
      compute='_compute_available_sessions',
      string=_("Sesiones disponibles"),
    )

    @api.depends('reason')
    def _compute_name(self):
        for record in self:
            if record.reason:
                # extrae la etiqueta legible ("Tutoría individual") en lugar del código ("TI")
                reason_label = dict(self._fields['reason'].selection).get(record.reason, record.reason)
                record.name = reason_label
            else:
                record.name = "Nueva Reserva"


    @api.onchange('booking_date', 'booking_resource_id', 'session_ids')
    def _compute_available_sessions(self):
      for record in self:
        if not record.booking_date or not record.booking_resource_id:
          record.available_session_ids = False
          continue

        weekday_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V'}
        day_code = weekday_map.get(record.booking_date.weekday())

        if not day_code:
          record.available_session_ids = False
          continue

        location_id = record.booking_resource_id.reservable_ref.location_id.id

        domain = [
            ('week_day', '=', day_code),
            ('location_id', '=', location_id),
            ('active', '=', True),
        ]

        origin_id = record._origin.id if record._origin else False

        # Excluir sesiones ya reservadas por otros para ese recurso y fecha
        existing_bookings = self.env['maya_booking.booking'].search([
            ('booking_date', '=', record.booking_date),
            ('booking_resource_id', '=', record.booking_resource_id.id),
            ('id', '!=', origin_id),
        ])
        booked_session_ids = existing_bookings.mapped('session_ids').ids
        if booked_session_ids:
            domain.append(('id', 'not in', booked_session_ids))

        # Consecutividad: solo la siguiente a la última seleccionada
        if record.session_ids:
            last_end_time = max(record.session_ids.mapped('end_time'))
            domain.append(('start_time', '=', last_end_time))

        record.available_session_ids = self.env['maya_core.session_schedule'].search(domain)



    """ def _onchange_filter_sessions(self):
      
      Filtra sesiones por:
      1. Día de la semana y ubicación.
      2. Disponibilidad (que no estén ya reservadas por otros).
      3. Continuidad (solo mostrar la siguiente a la última elegida).
      
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
      
      return {'domain': {'session_ids': domain}} """
    
    

    @api.depends('booking_date', 'session_ids.start_time', 'session_ids.end_time')
    def _compute_dates(self):
        for record in self:
            if record.booking_date and record.session_ids:
                # Ordenar sesiones para asegurar que cogemos el inicio real y el fin real
                start_hour = min(record.session_ids.mapped('start_time'))
                end_hour = max(record.session_ids.mapped('end_time'))

                record.date_start = self._combine_date_and_float(record.booking_date, start_hour)
                record.date_stop = self._combine_date_and_float(record.booking_date, end_hour)
            else:
                record.date_start = False
                record.date_stop = False

    def _combine_date_and_float(self, base_date, float_time):
        """
        Convierte una fecha y una hora float en un objeto Datetime UTC.
        """
        hours = int(float_time)
        minutes = int(round((float_time - hours) * 60))
        
        # 1. Creamos el datetime "ingenuo" (naive) con la hora local que queremos
        naive_dt = datetime.combine(base_date, datetime.min.time()).replace(
            hour=hours, minute=minutes
        )
        
        # 2. Obtenemos la zona horaria del usuario (o 'Europe/Madrid' por defecto)
        user_tz_name = self.env.user.tz or 'Europe/Madrid'
        user_tz = pytz.timezone(user_tz_name)
        
        # 3. Localizamos ese datetime (le decimos: "esta hora es CEST")
        # localize() es mejor que replace(tzinfo=...) para manejar cambios de horario verano/invierno
        local_dt = user_tz.localize(naive_dt)
        
        # 4. Lo convertimos a UTC y le quitamos la información de zona para que Odoo lo acepte
        # Odoo espera datetimes naive en la base de datos, asumiendo que son UTC
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)
    
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
    
    @api.constrains('booking_resource_id', 'date_stop')
    def _check_resource_is_bookable(self):
        for record in self:
            resource = record.booking_resource_id
            
            # Si el recurso está marcado como "No reservable" (is_bookable = False)
            if resource and not resource.is_bookable:
                
                # Buscamos el registro físico real (ej: maya_core.place) para ver su límite
                if resource.reservable_model and resource.reservable_id:
                    physical_record = self.env[resource.reservable_model].sudo().browse(resource.reservable_id)
                    
                    # Si el registro físico tiene fecha de última reserva guardada
                    if hasattr(physical_record, 'last_reservation_date') and physical_record.last_reservation_date:
                        
                        # Si nuestra reserva termina DESPUÉS de la fecha límite, bloqueamos
                        if record.date_stop and record.date_stop > physical_record.last_reservation_date:
                            
                            # Formateamos la fecha a la zona horaria del usuario para el mensaje de error
                            user_tz = pytz.timezone(self.env.user.tz or 'Europe/Madrid')
                            local_dt = pytz.utc.localize(physical_record.last_reservation_date).astimezone(user_tz)
                            formatted_date = local_dt.strftime('%d/%m/%Y a las %H:%M')
                            
                            raise ValidationError(
                                _("El recurso '%s' pasará a estar 'No Reservable'. Solo admite reservas que terminen antes del %s.") % 
                                (resource.resource_name, formatted_date)
                            )
                    else:
                        # Si no es reservable y no tiene fecha límite (nunca tuvo reservas o se limpió), se bloquea del todo
                        raise ValidationError(_("El recurso '%s' ha sido marcado como 'No Reservable' y no admite nuevas reservas.") % resource.resource_name)
                    
    @api.constrains('booking_date', 'booking_resource_id')
    def _check_max_days_in_advance(self):
        """
        Valida que la reserva no supere el límite de días de antelación
        configurado en el recurso físico (Place, Employee, etc.).
        """
        for record in self:
            if not record.booking_date or not record.booking_resource_id:
                continue

            resource = record.booking_resource_id
            
            # Buscamos el registro físico real para leer su configuración
            if resource.reservable_model and resource.reservable_id:
                physical_record = self.env[resource.reservable_model].sudo().browse(resource.reservable_id)
                
                # Verificamos que el recurso tenga el campo y que el límite sea mayor que 0 (0 = sin límite)
                if hasattr(physical_record, 'max_days_in_advance') and physical_record.max_days_in_advance > 0:
                    
                    # Obtenemos la fecha actual ajustada a la zona horaria del usuario
                    today = fields.Date.context_today(self)
                    
                    # Calculamos la diferencia en días
                    diferencia_dias = (record.booking_date - today).days
                    
                    if diferencia_dias > physical_record.max_days_in_advance:
                        
                        # Calculamos la fecha máxima exacta para dársela mascadita al usuario en el error
                        fecha_maxima = today + timedelta(days=physical_record.max_days_in_advance)
                        fecha_maxima_str = fecha_maxima.strftime('%d/%m/%Y')
                        
                        raise ValidationError(
                            _("No puedes reservar el recurso '%s' con más de %s días de antelación. "
                              "La fecha máxima permitida para este recurso es el %s.") % (
                                resource.resource_name, 
                                physical_record.max_days_in_advance,
                                fecha_maxima_str
                            )
                        )