# from odoo import http


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

