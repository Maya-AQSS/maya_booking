# from odoo import models, fields, api


# class maya_core(models.Model):
#     _name = 'maya_core.maya_core'
#     _description = 'maya_core.maya_core'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

