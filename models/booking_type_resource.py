# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingTypeResource(models.Model):
  """
  Interfaz polimórfico con varios tipos de recursos. 
  Permite asignar a un tipo de reserva una lista de BookingTypeResources, aunque cada uno de ellos
  apunte a un tipo de recurso diferente: empleado, espacio, material, puesto de trabajo...
  """

  _name = 'maya_booking.booking_type_resource'
  _description = 'Recursos reservables'

  type_id = fields.Many2one('maya_booking.booking_type', ondelete='cascade') 

  reservable_model = fields.Char(string="Modelo del recurso", required=True) # el modelo 
  reservable_id = fields.Integer(string="ID del recurso", required=True)  # el id del registro al que queremos apuntar

  reservable_ref = fields.Reference(
    selection='_get_reservable_models',   # devuelve lista de modelos permitidos
    string="Recurso físico",
    compute='_compute_reservable_ref', 
    # inverse='_inverse_reservable_ref', 
    store=True,
    required=True 
  )

  @api.model
  def _get_reservable_models(self):
    """
    Lista de modelos que pueden ser un recurso reservable
    """
    return [
      ('maya_core.place', 'Espacios'),
      ('res.partner', 'Contacto/Empresa (Prueba)'),
      ('maya_core.employee', 'Empleados'), 
    ]

  @api.depends('reservable_model', 'reservable_id')
  def _compute_reservable_ref(self):
    """
    Construye el Reference para la vista
    """
    for rec in self:
      if rec.reservable_model and rec.reservable_id:
        rec.reservable_ref = f"{rec.reservable_model},{rec.reservable_id}"
      else:
        rec.reservable_ref = False

  def _inverse_reservable_ref(self):
    """
    Guarda el modelo y el ID del recurso que el usuario elija en la BD
    """
    for rec in self:
      if rec.reservable_ref:
        rec.reservable_model = rec.reservable_ref._name
        rec.reservable_id = rec.reservable_ref.id
      else:
        rec.reservable_model = False
        rec.reservable_id = 0