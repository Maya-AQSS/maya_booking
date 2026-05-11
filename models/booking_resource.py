# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingResource(models.Model):
  """
  Interfaz polimórfico con varios tipos de recursos. 
  Permite asignar a un tipo de reserva una lista de BookingTypeResources, aunque cada uno de ellos
  apunte a un tipo de recurso diferente: empleado, espacio, material, puesto de trabajo...
  """

  _name = 'maya_booking.booking_resource'
  _description = 'Recursos reservables'

  booking_type_ids = fields.Many2many('maya_booking.booking_type', string = 'Tipos de reserva', help = 'Tipos de reserva en los que aparece este recurso',ondelete='cascade') 

  reservable_model = fields.Char(string="Modelo del recurso", required=True) # el modelo 
  reservable_id = fields.Integer(string="ID del recurso", required=True)  # el id del registro al que queremos apuntar

  reservable_ref = fields.Reference(
    selection='_get_reservable_models',   # devuelve lista de modelos permitidos
    string="Recurso físico",
    compute='_compute_reservable_ref', 
    # inverse='_inverse_reservable_ref', 
    store=True
  )
  
  resource_name = fields.Char(string="Descripción del recurso", compute="_compute_resource_name", store = True)

  # Nuevo campo espejo (no hace falta mostrarlo en ninguna vista)
  is_bookable = fields.Boolean(
      string="Es reservable (Copia)",
      compute="_compute_is_bookable",
      store=True,
      default=True
  )

  @api.depends('reservable_model', 'reservable_id')
  def _compute_is_bookable(self):
      for rec in self:
          if rec.reservable_model and rec.reservable_id:
              # Busca el registro físico real
              real_record = self.env[rec.reservable_model].sudo().browse(rec.reservable_id)
              if real_record.exists() and 'bookable' in real_record._fields:
                  rec.is_bookable = real_record.bookable
              else:
                  rec.is_bookable = False
          else:
              rec.is_bookable = False

  @api.model
  def _get_reservable_models(self):
    """
    Lista de modelos que pueden ser un recurso reservable
    """
    return [
      ('maya_core.place', 'Espacios'),
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

  @api.depends('reservable_ref')
  def _compute_resource_name(self):
    for record in self:
      # Verificamos que exista la referencia y que el registro referenciado no haya sido borrado
      if record.reservable_ref and record.reservable_ref.exists():
        record.resource_name = record.reservable_ref.display_name
      else:
        record.resource_name = _("Sin recurso")