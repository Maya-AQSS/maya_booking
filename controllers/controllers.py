from odoo import http
from odoo.http import request

class MayaBookingApi(http.Controller):

    @http.route('/api/booking_types', type='json', auth='public', methods=['POST'], csrf=False)
    def get_booking_types(self, **kwargs):
        """
        Devuelve los tipos de reserva publicados para usarlos fuera del ERP.
        """
        domain = [('published', '=', True)]
        tipos_reserva = request.env['maya_booking.booking_type'].sudo().search(domain)

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        data = []
        for rec in tipos_reserva:
            image_url = False
            if hasattr(rec, 'image_icon') and rec.image_icon:
                image_url = f"{base_url}/web/image/maya_booking.booking_type/{rec.id}/image_icon"

            data.append({
                'id': rec.id,
                'name': rec.name,
                'description': rec.description or '',
                'duration': rec.duration,
                'resource_type': rec.resource_type,
                'resource_count': rec.resource_count,
                'resource_ids': rec.resource_ids.ids, 
                'image_url': image_url,
            })

        return {
            'status': 200,
            'message': 'Success',
            'data': data
        }
# class MayaCore(http.Controller):
#     @http.route('/maya_core/maya_core', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/maya_core/maya_core/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('maya_core.listing', {
#             'root': '/maya_core/maya_core',
#             'objects': http.request.env['maya_core.maya_core'].search([]),
#         })

#     @http.route('/maya_core/maya_core/objects/<model("maya_core.maya_core"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('maya_core.object', {
#             'object': obj
#         })

