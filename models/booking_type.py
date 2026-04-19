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
    published = fields.Boolean(_('Publicado'), default=False)

    resource_ids = fields.Many2many('maya_booking.booking_resource', string='Recursos asociados', help='Recursos asociados a este tipo de reserva',
                                     domain="[('reservable_model', '=', resource_model)]"  )
    
    resource_count = fields.Integer(
        compute='_compute_resource_count',
        string=_('Cantidad de recursos')
    )
    
    resource_model = fields.Char(
        compute='_compute_resource_model',
        string=_('Modelo de recurso'),
    )

    """ bookable_resource_ids = fields.Many2many(
        'maya_booking.resource',
        string=_('Recursos disponibles'),
        domain="[('model_name', '=', resource_model)]"  
    ) """

    # computed para mostrar cuántos recursos tiene asociados
    resource_count = fields.Integer(compute='_compute_resource_count')  

    @api.depends('resource_ids')
    def _compute_resource_count(self):
      for record in self:
        record.resource_count = len(record.resource_ids)

    @api.depends('resource_type')
    def _compute_resource_model(self):
      modelo_map = {
          'E': 'maya_core.employee',                    
          'S': 'maya_core.place',           
          #'W': 'maya_booking.workstation',       
          #'I': 'maya_booking.equipment',         
      }
      for record in self:
        record.resource_model = modelo_map.get(record.resource_type, '')
    
    """ @api.constrains('bookable_resource_ids')
    def _check_same_model(self):
      for record in self:
        if record.bookable_resource_ids:
          modelos = record.bookable_resource_ids.mapped('model_name')
          if len(set(modelos)) > 1:
            raise ValidationError(
                _('No se pueden mezclar diferentes tipos de recursos. '
                  'Todos los recursos deben ser del mismo modelo.')
            )  """

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
        # filtro para mostrar solo las reservas de este tipo de recurso
        'domain': [('booking_resource_id.booking_type_ids.resource_type', '=', self.resource_type)],
        'context': {
            # incluyo una variable en el contexto para poder filtrar los recursos de tipo de reserva seleccionado
            'timeline_booking_type_id': self.id,  
        }
      }