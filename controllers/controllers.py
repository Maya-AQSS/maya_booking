from odoo import http, fields
from odoo.http import request
from datetime import timedelta

class MayaBookingApi(http.Controller):

    @http.route('/api/maya_booking/resources/search', type='json', auth='public', methods=['POST'], csrf=False)
    def search_resources_reservable(self, **kwargs):
        booking_type_id = kwargs.get('booking_type_id')
        tag_codes = kwargs.get('tag_codes', [])
        limit = kwargs.get('limit', 10)
        
        if not booking_type_id:
            return {'status': 400, 'message': 'Se requiere booking_type_id numérico.', 'data': []}

        # busca el tipo de reserva y validamos que exista y esté publicado
        booking_type = request.env['maya_booking.booking_type'].sudo().browse(booking_type_id)
        if not booking_type.exists() or not booking_type.published:
            return {'status': 404, 'message': 'El tipo de reserva no existe o no está publicado.', 'data': []}

        # busca las etiquetas por adelantado
        tags = request.env['maya_core.tag'].sudo().search([('code', 'in', tag_codes)]) if tag_codes else False
        if tag_codes and not tags:
            return {'status': 404, 'message': 'Etiquetas no encontradas en el sistema.', 'data': []}

        data = []
        today = fields.Date.context_today(request.env.user)
        weekday_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V'}

        # Itera sobre TODOS los recursos vinculados a este tipo de reserva
        for br in booking_type.resource_ids:
            if len(data) >= limit:
                break
                
            if not br.reservable_model or not br.reservable_id:
                continue

            # Obtiene el registro físico 
            phys_rec = request.env[br.reservable_model].sudo().browse(br.reservable_id)
            if not phys_rec.exists():
                continue

            if tags:
                # Si el modelo físico no tiene el campo 'tag_ids' y el usuario filtró por tags, se descarta
                if not hasattr(phys_rec, 'tag_ids'):
                    continue
                
                # Comprueba que el recurso físico tenga TODAS las etiquetas solicitadas
                phys_tag_ids = phys_rec.tag_ids.ids
                if not all(t.id in phys_tag_ids for t in tags):
                    continue

            # Como todos heredan de ReservableMixin, podemos consultar session_schedule_ids con seguridad
            if not phys_rec.session_schedule_ids:
                continue

            sessions_by_day = {}
            for s in phys_rec.session_schedule_ids:
                sessions_by_day.setdefault(s.week_day, []).append(s.id)

           
            # Si el recurso tiene > 0, manda el recurso, si es 0 se usa el valor del booking_type
            effective_advance_days = phys_rec.max_days_in_advance if phys_rec.max_days_in_advance > 0 else booking_type.max_days_in_advance
            effective_max_consec = phys_rec.num_max_session_consecutive if phys_rec.num_max_session_consecutive > 0 else booking_type.num_max_session_consecutive

            has_free_slot = False
            
            days_to_check = effective_advance_days if effective_advance_days > 0 else 30

            for i in range(days_to_check):
                check_date = today + timedelta(days=i)
                
                if not phys_rec.bookable and phys_rec.last_reservation_date:
                    if check_date > phys_rec.last_reservation_date.date():
                        break 
                elif not phys_rec.bookable and not phys_rec.last_reservation_date:
                    break # El recurso está bloqueado definitivamente

                day_code = weekday_map.get(check_date.weekday())
                if not day_code or day_code not in sessions_by_day:
                    continue

                possible_sessions = set(sessions_by_day[day_code])

                # Busca si hay reservas que pisen este recurso concreto en este día
                bookings = request.env['maya_booking.booking'].sudo().search([
                    ('booking_resource_id', '=', br.id),
                    ('booking_date', '=', check_date)
                ])
                booked_sessions = set(bookings.mapped('session_ids').ids)

                if possible_sessions - booked_sessions:
                    has_free_slot = True
                    break 

            if not has_free_slot:
                continue

            res_dict = {
                'booking_resource_id': br.id, 
                'name': phys_rec.display_name if hasattr(phys_rec, 'display_name') else br.resource_name,
                'resource_model': br.reservable_model, # Indica si es un espacio, empleado, etc.
                'max_consecutive': effective_max_consec,
                'advance_days': effective_advance_days,
                'is_closing_soon': not phys_rec.bookable
            }

            if hasattr(phys_rec, 'location_id') and phys_rec.location_id:
                res_dict['location'] = phys_rec.location_id.name

            if hasattr(phys_rec, 'tag_ids') and phys_rec.tag_ids:
                res_dict['tags'] = [{'name': t.name, 'code': t.code} for t in phys_rec.tag_ids]
            else:
                res_dict['tags'] = []

            data.append(res_dict)

        return {
            'status': 200,
            'message': f'Encontrados {len(data)} recursos aptos.',
            'data': data
        }