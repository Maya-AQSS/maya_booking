from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ReservableResource(models.Model):
    _inherit = 'maya_booking.resource'
    
    def action_mark_as_not_reservable(self):
        for rec in self:
            if rec._has_active_bookings():
                rec.write({
                    'bookable': False,
                    'last_reservation_date': fields.Datetime.now()
                })
            else:
                rec.unlink()
    
    def _has_active_bookings(self):
        Booking = self.env.get('maya_booking.booking')
        if Booking:
            active_states = ['draft', 'confirmed', 'in_progress']
            count = Booking.search_count([
                ('resource_id', '=', self.id),
                ('state', 'in', active_states)
            ])
            return count > 0
        return False
    
    @api.constrains('bookable')
    def _check_bookable_with_bookings(self):
        for rec in self:
            if not rec.bookable and rec._has_active_bookings():
                raise ValidationError(
                    f'No se puede desmarcar "{rec.name}" como reservable '
                    f'porque tiene reservas activas pendientes.'
                )