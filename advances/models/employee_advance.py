# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, exceptions
import datetime
from odoo.exceptions import ValidationError
from dateutil import relativedelta

class EmployeeAdvance(models.Model):
    _name = 'employee.advance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))
    employee_id=fields.Many2one('hr.employee',required=True, readonly=True, states={'draft': [('readonly', False)]},string="الموظف")
    employee_id1=fields.Many2one('hr.employee',required=True, readonly=True, states={'draft': [('readonly', False)]},string="موظف1")
    employee_id2=fields.Many2one('hr.employee',required=True, readonly=True, states={'draft': [('readonly', False)]},string="موظف2")
    department_id=fields.Many2one('hr.department',string='القسم',related='employee_id.department_id',store=True)
    date=fields.Date(required=True, readonly=True, states={'draft': [('readonly', False)]},string='التاريخ')
    amount=fields.Float(string='المبلغ',readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Create By', index=True, tracking=2, default=lambda self: self.env.user)

    state=fields.Selection([
        ('draft','جديد'),
        ('confirm','تأكيد')
        ,('cancel','الغاء')
    ],default='draft',string='الحاله')

    @api.model
    def create(self, vals):
        res=super(EmployeeAdvance, self).create(vals)
        if res.name == 'New':
            res.name = self.env['ir.sequence'].next_by_code('employee.advance') or 'New'
        res.employee_id1.activity_schedule('advances.schdule_activity_advance_id', res.date, user_id=self.env.user.id,
            summary=str(res.amount/2)+'وعليه في حاله تهرب هذا الموظف من سداد السلفه فعليك بدفع نص مبلغ السلفه والتي تبلغ'+str(res.employee_id.name)+'للموظف' +str(res.employee_id2.name)+'تم وضعك كضامن ومعك الموظف'
                    )
        res.employee_id2.activity_schedule('advances.schdule_activity_advance_id', res.date, user_id=self.env.user.id,
            summary=str(res.amount/2)+'وعليه في حاله تهرب هذا الموظف من سداد السلفه فعليك بدفع نص مبلغ السلفه والتي تبلغ'+str(res.employee_id.name)+'للموظف' +str(res.employee_id1.name)+'تم وضعك كضامن ومعك الموظف'
                    )

        return res

    @api.constrains('amount','employee_id','employee_id1','employee_id2','department_id','date')
    def amount_accept(self):
        for rec in self:
            advance_depart=self.env['advance.departments.line'].search([('department_id','=',rec.department_id.id),('date_to','>=',rec.date),('date','<=',rec.date),('state','=','approve')])
            advance_emp=self.search([('employee_id','=',rec.employee_id.id),('date','<=',rec.date),('id','!=',rec.id)])
            contract=self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id)],limit=1)
            if rec.amount <= 0.0 :
                raise ValidationError(_('المبلغ لا يجب أن يكون صفر أو أقل من الصفر'))
            elif rec.amount > advance_depart.amount :
                raise ValidationError(_('المبلغ المطلوب للسلفه  لا يجب أن يزيد عن الحد الأقصى المحدد لقسم '+'%s' +' '+'والذي يبلغ'+' '+  '%s')%(rec.department_id.name,advance_depart.amount))

            elif rec.amount > contract.wage :
                raise ValidationError(_('المبلغ المطلوب للسلفه  لا يجب أن يزيد عن مرتب الموظف  %s  والذي يبلغ %s ')%(rec.employee_id.name,contract.wage))
            for i in advance_emp:
                if relativedelta.relativedelta(rec.date,i.date).months < 6 :
                    raise ValidationError(
                        _('هذا الموظف %s لا يستطيع طلب سلفه وذلك لطلبه سلفه من مده تقل عن 6 أشهر') % (
                        rec.employee_id.name))

            if rec.employee_id1 == rec.employee_id or rec.employee_id2 == rec.employee_id :
                raise ValidationError(_('الموظف %s لا يمكن أن يكون ضامن لنفسه')%(rec.employee_id.name))

            if rec.employee_id1 == rec.employee_id2 :
                raise ValidationError(_('الموظف الأول والثاني يجب أن يكونوا مختلفين'))


    def set_to_draft(self):
        for rec in self:
          rec.write({'state': 'draft'})


    def cancel(self):
        for rec in self:
            advance_depart = self.env['advance.departments.line'].search(
                [('department_id', '=', rec.department_id.id), ('date_to', '>=', rec.date), ('date', '<=', rec.date),
                 ('state', '=', 'approve')])

            advance_depart.write({'amount': advance_depart.amount + rec.amount})
            rec.employee_id.activity_schedule('advances.schdule_activity_advance_id', rec.date, user_id=self.env.user.id,
                                  summary='تم رفض طلب السلفه التي طلبت بتاريخ '+str(rec.date))


            rec.write({'state': 'cancel'})


    def confirm(self):
        for rec in self:
            advance_depart = self.env['advance.departments.line'].search(
                [('department_id', '=', rec.department_id.id), ('date_to', '>=', rec.date), ('date', '<=', rec.date),('state','=','approve')])

            rec.write({'state': 'confirm'})
            advance_depart.write({'amount':advance_depart.amount - rec.amount})
            rec.employee_id.activity_schedule('advances.schdule_activity_advance_id', rec.date, user_id=self.env.user.id,
                                  summary='تم قبول طلب السلفه التي طلبت بتاريخ '+str(rec.date))

    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise ValidationError(_("لا يمكنك مسح سلفه تم الموافقه عليها"))

        return  super(EmployeeAdvance, self).unlink()


