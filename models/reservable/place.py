from odoo import models, fields

class Place(models.Model):
    _inherit = ['maya_core.place', 'maya_booking.reservable.mixin']
