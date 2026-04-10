# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BookingType(models.Model):
    _name = 'maya_booking.booking_type'
    _description = 'Tipos de Recurso'

    name = fields.Char(_('Nombre'), required=True, translate=True, help=_('Nombre del recurso'))
    description = fields.Char(_('Descripción'), translate=True, help=_('Descripción del recurso'))
    duration = fields.Float(default=1.0)
    resource_type = fields.Selection([
        ('E', 'Empleado'),
        ('S', 'Espacio'),
        ('W', 'Puesto'),
        ('I', 'Elemento de inventario'),
    ], default='S')

    resource_ids = fields.One2many('maya_booking.booking_type_resource', 'type_id')

    bookable_resource_ids = fields.Many2many(
        'maya_booking.resource',
        string=_('Recursos disponibles'),
    )

    resource_count = fields.Integer(compute='_compute_resource_count')

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for record in self:
            record.resource_count = len(record.resource_ids)

    @api.constrains('bookable_resource_ids')
    def _check_same_model(self):
        for record in self:
            model_names = record.bookable_resource_ids.mapped('model_name')
            modelos_unicos = set(model_names)
            if len(modelos_unicos) > 1:
                raise ValidationError(
                    _('No se pueden mezclar diferentes tipos de recursos. '
                      'Todos los recursos deben ser del mismo modelo.')
                )

    def action_open_timeline(self):
        self.ensure_one()
        return {
            'name': f'Calendario: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'maya_booking.booking_example',
            'view_mode': 'timeline,list,form',
            'domain': [('resource_id.type_id', '=', self.id)],
            'context': {}
        }