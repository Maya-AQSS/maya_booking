# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ReservableMixin(models.AbstractModel):
    _name = 'maya_booking.reservable.mixin'
    _description = 'Mixin reservables'

    bookable = fields.Boolean(default=True, string='Es reservable')
    
    resource_type = fields.Selection([
        ('E', 'Empleado'),
        ('S', 'Espacio'),
        ('W', 'Puesto'),
        ('I', 'Elemento de inventario'),
    ], string='Tipo de recurso', default='S')
    
    num_max_session_consecutive = fields.Integer(string='Número máximo de sesiones consecutivas', 
                                                 help="Número máximo de sesiones consecutivas que se pueden reservar. 0: Sin límite (hasta final del día)",
                                               default=2)

    max_days_in_advance = fields.Integer(string='Reserva con antelación (días)', 
                                         help="Máximos días de antelación con los que se puede realizar una reserva. 0: sin límite", default=15)
    
    booking_limit_date = fields.Date(string='Fecha límite de reserva')

    session_schedule_ids = fields.Many2many(
        "maya_core.session_schedule",
        string=_("Horarios posibles de reserva"),
        help=_("Consultar las reservas para ver la disponibilidad"),
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._sync_resource()
        return records
    
    def write(self, vals):
        if 'bookable' in vals and vals.get('bookable') == False:
            for record in self:
                if record._has_active_bookings():
                    raise ValidationError('No se puede desmarcar porque tiene reservas activas')
        
        result = super().write(vals)
        
        if 'bookable' in vals:
            for record in self:
                record._sync_resource()
        
        return result
    
    def _sync_resource(self):
        Resource = self.env['maya_booking.resource']
        
        existing = Resource.search([
            ('model_name', '=', self._name),
            ('res_id', '=', self.id)
        ], limit=1)
        
        if self.bookable:
            valores = {
                'name': self.name,
                'model_name': self._name,
                'res_id': self.id,
                'bookable': True,
                'booking_limit_date': self.booking_limit_date,
            }
            if existing:
                existing.write(valores)
            else:
                Resource.create(valores)
        else:
            if existing:
                if self._has_active_bookings():
                    existing.write({
                        'bookable': False,
                        'last_reservation_date': fields.Datetime.now()
                    })
                else:
                    existing.unlink()
    
    def _has_active_bookings(self):
        resource = self.env['maya_booking.resource'].search([
            ('model_name', '=', self._name),
            ('res_id', '=', self.id)
        ], limit=1)
        
        if not resource:
            return False
        
        reservas = self.env['maya_booking.booking'].search_count([
            ('resource_id', '=', resource.id),
            ('state', 'in', ['draft', 'confirmed', 'in_progress'])
        ])
        
        return reservas > 0
    
    @api.constrains('resource_type')
    def _check_resource_type(self):
        for record in self:
            tipos_validos = ['E', 'S', 'W', 'I']
            if record.resource_type not in tipos_validos:
                raise ValidationError('Tipo de recurso no válido')