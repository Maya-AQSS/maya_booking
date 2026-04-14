from odoo import models, fields

class Place(models.Model):
    _name = 'maya_core.place'
    _inherit = ['maya_booking.place', 'maya_booking.reservable.mixin']
