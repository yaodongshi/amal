from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
import base64
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    branch_id = fields.Many2one('res.branch', related='employee_id.branch_id', store=True, copy=False)

    def action_payslip_done(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            payslip.move_id.write({'branch_id': payslip.branch_id.id})
        return res
