# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingType(models.Model):
    """
    Define los tipos de reservas
    """

    _name = 'maya_booking.booking_type'
    _description = 'Tipos de reserva'

    name = fields.Char(_('Nombre'), required = True, translate = True, help=_('Nombre del tipo de reserva'))
    description = fields.Char(_('Descripción'), translate = True, help=_('Descripción del tipo de reserva'))
    duration = fields.Float(default=1.0)          # horas por defecto
    resource_type = fields.Selection([            # opcional para filtrar    
        ('E', 'Empleado'),     
        ('S', 'Espacio'),    
        ('W', 'Puesto'),     
        ('I', 'Elemento de inventario'), ], 
        default='S') 
    resource_ids = fields.One2many('maya_booking.booking_type_resource', 'type_id')

    # computed para mostrar cuántos recursos tiene asociados
    resource_count = fields.Integer(compute='_compute_resource_count')  

    @api.depends('resource_ids')
    def _compute_resource_count(self):
      for record in self:
        record.resource_count = len(record.resource_ids)

    def action_open_timeline(self):
      """
      Abre la vista timeline desde el kanban
      """
      self.ensure_one() 
    
      return {
        'name': f'Calendario: {self.name}',
        'type': 'ir.actions.act_window',
        'res_model': 'maya_booking.booking', 
        'view_mode': 'timeline,list,form',
        #filtro para mostrar solo las reservas de este tipo de recurso
        'domain': [('resource_id.type_id', '=', self.id)],
        'context': {}
      }