from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    branch_id = fields.Many2one('res.branch', related='employee_id.branch_id', store=True, copy=False)
