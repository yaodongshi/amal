# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class HrPayslip(models.Model):
    _inherit ='hr.payslip'
    advance=fields.Float()
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res=super(HrPayslip, self)._onchange_employee()
        advance = 0
        for rec in self:
            advance_depart = self.env['employee.advance'].search(
            [('employee_id', '=', rec.employee_id.id), ('date', '>=', rec.date_from), ('date', '<=', rec.date_to),
             ('state', '=', 'confirm')])
            for i in advance_depart:
                advance += i.amount
            rec.advance =advance

        return res

    def _get_new_input_lines(self):
        res=[]
        lines = {}
        other_input = self.env['hr.payslip.input.type'].search([('struct_ids','in',[self.struct_id.id])])
        for line in other_input:
            if line.advance == False :
               lines = {
                'input_type_id': line.id,
                'amount': 0.0,
                }
            else:
               lines = {
                'input_type_id': line.id,
                'amount':self.advance,
                }
            res.append(lines)
        if self.struct_id:
            input_line_values =res
            input_lines = self.input_line_ids.browse([])
            for r in input_line_values:
                input_lines |= input_lines.new(r)
            return input_lines
        else:
            return [(5, False, False)]



class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'
    advance=fields.Boolean('سلف')
