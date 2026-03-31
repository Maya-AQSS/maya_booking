# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingType(models.Model):
    """
    Define los tipos de recursos reservables
    """

    _name = 'maya_booking.booking_type'
    _description = 'Tipos de Recurso'

    name = fields.Char(_('Nombre'), required = True, translate = True, help=_('Nombre del recurso'))
    description = fields.Char(_('Descripción'), translate = True, help=_('Descripción del recurso'))
    duration = fields.Float(default=1.0)          # horas estandar
    resource_type = fields.Selection([            # opcional para filtrar    
        ('E', 'Empleado'),     
        ('S', 'Espacio'),    
        ('W', 'Puesto'),     
        ('I', 'Elemento de inventario'), ], 
        default='S') 
    resource_ids = fields.One2many('maya_booking.booking_type_resource', 'type_id')

    # #  computed para mostrar cuántos recursos tiene asociados
    resource_count = fields.Integer(compute='_compute_resource_count')  

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for record in self:
            record.resource_count = len(record.resource_ids)