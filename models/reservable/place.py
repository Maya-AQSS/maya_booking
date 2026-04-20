from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Place(models.Model):
  _name = 'maya_core.place'
  _inherit = ['maya_core.place', 'maya_booking.reservable.mixin']

  availability_grid_html = fields.Html(
            string="Cuadrante de Horarios", 
            compute="_compute_availability_grid_html",
            sanitize=False)

  @api.depends('name', 'location_id')
  def _compute_display_name(self):
    for record in self:
      if record == False or record.name == False or record.location_id == False:
        record.display_name = ""
      else:
        record.display_name = record.name + " - [" + record.location_id.name + "]"


  def unlink(self):
    for record in self:
      reservas = self.env["maya_booking.booking"].search_count(
        [("place_id", "=", record.id)]
      )
      if reservas > 0:
        raise UserError(
            _("No se puede eliminar el espacio '%s' porque tiene reservas asociadas.") % record.name)

    @api.depends('location_id', 'session_schedule_ids')
    def _compute_availability_grid_html(self):
        for record in self:
            if not record.location_id:
                record.availability_grid_html = "<div class='alert alert-warning'>Seleccione una ubicación para cargar el cuadrante.</div>"
                continue

            # Todas las sesiones posibles de la ubicación
            all_location_schedules = self.env['maya_core.session_schedule'].search([
                ('location_id', '=', record.location_id.id),
                ('active', '=', True)
            ])

            # IDs de las sesiones previamente asignadas a este espacio
            assigned_ids = record.session_schedule_ids.ids

            days = ['0L', '1M', '2X', '3J', '4V']
            schedules_by_day = {day: [] for day in days}
            
            for schedule in all_location_schedules:
                # Calculamos horas
                start_h = int(schedule.start_time)
                start_m = int(round((schedule.start_time - start_h) * 60))
                end_h = int(schedule.end_time)
                end_m = int(round((schedule.end_time - end_h) * 60))
                
                schedules_by_day[schedule.week_day].append({
                    'name': schedule.name,
                    'time_str': f"{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d}",
                    'start_time': schedule.start_time,
                    'is_assigned': schedule.id in assigned_ids 
                })

            for day in days:
                schedules_by_day[day] = sorted(schedules_by_day[day], key=lambda x: x['start_time'])

            values = {
                'days': days,
                'day_names': {'0L': 'Lunes', '1M': 'Martes', '2X': 'Miércoles', '3J': 'Jueves', '4V': 'Viernes'},
                'schedules_by_day': schedules_by_day,
            }

            record.availability_grid_html = self.env['ir.qweb']._render('maya_booking.template_cuadrante_horarios', values)