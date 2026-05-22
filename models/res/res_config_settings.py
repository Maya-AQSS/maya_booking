# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    num_max_session_consecutive = fields.Integer(
    string='Máximo sesiones', 
    config_parameter='maya_booking.num_max_session_consecutive',
    default='2',
    help="Valor por defecto"
    )

    max_days_in_advance = fields.Integer(
        string='Días antelación', 
        config_parameter='maya_booking.max_days_in_advance',
        default='15',
        help="Valor por defecto"
    )