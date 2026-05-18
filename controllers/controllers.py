from odoo import http, fields
from odoo.http import request
from datetime import timedelta

class MayaBookingApi(http.Controller):

    @http.route('/api/maya_booking/resources/search', type='json', auth='public', methods=['POST'], csrf=False)
    def search_resources_reservable(self, booking_type_id=None, tag_codes=None, limit=3, date=None, date_from=None, date_to=None, **kwargs):
        
        b_type_id = booking_type_id or kwargs.get('booking_type_id')
        t_codes = tag_codes or kwargs.get('tag_codes', [])
        lim = limit or kwargs.get('limit', 3)
        
        date_str = date or kwargs.get('date')
        date_from_str = date_from or kwargs.get('date_from')
        date_to_str = date_to or kwargs.get('date_to')

        if not b_type_id:
            return {'status': 400, 'message': 'Se requiere booking_type_id numérico.', 'data': []}

        # Validar tipo de reserva
        booking_type = request.env['maya_booking.booking_type'].sudo().browse(b_type_id)
        if not booking_type.exists() or not booking_type.published:
            return {'status': 404, 'message': 'El tipo de reserva no existe o no está publicado.', 'data': []}

        # Validar etiquetas
        tags = request.env['maya_core.tag'].sudo().search([('code', 'in', t_codes)]) if t_codes else False
        if t_codes and not tags:
            return {'status': 404, 'message': 'Etiquetas no encontradas en el sistema.', 'data': []}

        today = fields.Date.context_today(request.env.user)
        
        if date_str:
            start_date = fields.Date.to_date(date_str)
            end_date = start_date
        elif date_from_str and date_to_str:
            start_date = fields.Date.to_date(date_from_str)
            end_date = fields.Date.to_date(date_to_str)
        else:
            start_date = today
            end_date = None 

        if end_date and start_date > end_date:
            return {'status': 400, 'message': 'La fecha de inicio no puede ser posterior a la de fin.', 'data': []}

        valid_resources_info = []
        max_advance_global = 0

        for br in booking_type.resource_ids:
            if not br.reservable_model or not br.reservable_id:
                continue

            phys_rec = request.env[br.reservable_model].sudo().browse(br.reservable_id)
            if not phys_rec.exists() or not phys_rec.session_schedule_ids:
                continue

            # Filtro etiquetas
            if tags:
                if not hasattr(phys_rec, 'tag_ids'):
                    continue
                phys_tag_ids = phys_rec.tag_ids.ids
                if not all(t.id in phys_tag_ids for t in tags):
                    continue

            advance_days = phys_rec.max_days_in_advance if phys_rec.max_days_in_advance > 0 else 30
            if advance_days > max_advance_global:
                max_advance_global = advance_days

            valid_resources_info.append({
                'br': br,
                'phys_rec': phys_rec,
                'advance_days': advance_days
            })

        if not valid_resources_info:
            return {'status': 200, 'message': 'No se encontraron recursos aptos.', 'data': []}

        global_end_date = end_date if end_date else start_date + timedelta(days=max_advance_global)
        valid_br_ids = [r['br'].id for r in valid_resources_info]
        
        all_bookings = request.env['maya_booking.booking'].sudo().search([
            ('booking_resource_id', 'in', valid_br_ids),
            ('booking_date', '>=', start_date),
            ('booking_date', '<=', global_end_date)
        ])

        bookings_map = {}
        for b in all_bookings:
            b_date = b.booking_date
            b_date_str = b_date.strftime('%Y-%m-%d') if hasattr(b_date, 'strftime') else str(b_date)[:10]
            key = (b.booking_resource_id.id, b_date_str)
            bookings_map.setdefault(key, set()).update(b.mapped('session_ids').ids)

        data = []
        weekday_map = {0: '0L', 1: '1M', 2: '2X', 3: '3J', 4: '4V', 5: '5S', 6: '6D'}

        for r_info in valid_resources_info:
            if len(data) >= lim:
                break

            br = r_info['br']
            phys_rec = r_info['phys_rec']
            advance_days = r_info['advance_days']

            sessions_by_day = {}
            for s in phys_rec.session_schedule_ids:
                sessions_by_day.setdefault(s.week_day, []).append({
                    'id': s.id,
                    'name': s.display_name if hasattr(s, 'display_name') else s.name
                })

            resource_end_date = end_date if end_date else today + timedelta(days=advance_days)
            available_slots = []
            
            days_to_iterate = (resource_end_date - start_date).days + 1

            for i in range(days_to_iterate):
                check_date = start_date + timedelta(days=i)
                check_date_str = check_date.strftime('%Y-%m-%d')
                
                if not phys_rec.bookable:
                    if phys_rec.last_reservation_date and check_date > phys_rec.last_reservation_date.date():
                        continue
                    elif not phys_rec.last_reservation_date:
                        continue

                day_code = weekday_map.get(check_date.weekday())
                if not day_code or day_code not in sessions_by_day:
                    continue

                day_sessions_info = sessions_by_day[day_code]
                possible_session_ids = set(s['id'] for s in day_sessions_info)

                booked_session_ids = bookings_map.get((br.id, check_date_str), set())
                free_session_ids = possible_session_ids - booked_session_ids

                if free_session_ids:
                    free_sessions_info = [s for s in day_sessions_info if s['id'] in free_session_ids]
                    available_slots.append({
                        'date': check_date_str,
                        'sessions': free_sessions_info
                    })

            if available_slots:
                res_dict = {
                    'booking_resource_id': br.id, 
                    'name': phys_rec.display_name if hasattr(phys_rec, 'display_name') else br.resource_name,
                    'resource_model': br.reservable_model,
                    'max_consecutive': phys_rec.num_max_session_consecutive,
                    'advance_days': advance_days,
                    'is_closing_soon': not phys_rec.bookable,
                    'available_slots': available_slots
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
            'message': f'Encontrados {len(data)} recursos aptos con disponibilidad.',
            'data': data
        }