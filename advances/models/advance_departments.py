# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, exceptions
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AdvanceDepartments(models.Model):
    _name = 'advance.departments'
    _rec_name= 'date'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    user_id = fields.Many2one('res.users',string='Create By', index=True, tracking=2, default=lambda self: self.env.user)
    date=fields.Date(required=True,readonly=True, states={'draft': [('readonly', False)]},string='التاريخ')
    date_to=fields.Date(compute='_date_to',store=True,string='الى تاريخ')
    advance_lines_id=fields.One2many('advance.departments.line','advance_id',required=True,readonly=True, states={'draft': [('readonly', False)]})
    amount=fields.Float(compute='_amount',store=True,string='المبلغ الاجمالي')
    state=fields.Selection([
        ('draft','جديد'),
        ('approve','تأكيد')
        ,('cancel','الغاء')
    ],default='draft',string='الحاله')




    @api.depends('date')
    def _date_to(self):
        for rec in self:
            if rec.date != False:
                rec.date_to= rec.date + relativedelta(months=6)


    @api.constrains('date')
    def _date_constrain(self):
        for rec in self:
            if rec.date != False:
                depart=self.search([('date','>=',rec.date),('date_to','<=',rec.date_to),('id','!=',rec.id)])
                depart1=self.search([('date','>=',rec.date),('date_to','>=',rec.date_to),('id','!=',rec.id)])
                depart2=self.search([('date','<',rec.date),('date_to','>=',rec.date_to),('id','!=',rec.id)])
                if depart or depart1 or depart2:
                    raise ValidationError(_('لا تستطيع انشاء قسم سلفه بنفس الفتره'))

    @api.depends('advance_lines_id','advance_lines_id.amount')
    def _amount(self):
        for depart in self:
            total = 0.0
            for line in depart.advance_lines_id:
                total += line.amount
            depart.amount = total




    def set_to_draft(self):
        for rec in self:
          rec.write({'state': 'draft'})

    def cancel(self):
        for rec in self:
          rec.write({'state': 'cancel'})


    def approve(self):
        for rec in self:
            rec.write({'state': 'approve'})

    def unlink(self):
        for rec in self:
            if rec.state == 'approve':
                raise ValidationError(_("لا يمكنك مسح قسم سلفه تم الموافقه عليها"))

        return  super(AdvanceDepartments, self).unlink()



class AdvanceDepartmentsline(models.Model):
    _name = 'advance.departments.line'
    advance_id=fields.Many2one('advance.departments')
    date=fields.Date(related='advance_id.date',store=True)
    date_to=fields.Date(related='advance_id.date_to',store=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('approve','Approve')
        ,('cancel','Cancel')
    ],default='draft',string= 'الحاله',related='advance_id.state',store=True)

    department_id=fields.Many2one('hr.department',required=True,string='القسم')
    amount=fields.Float('المبلغ')

    @api.constrains('amount')
    def amount_accept(self):
        for rec in self:
            if rec.amount <= 0.0 and self.env.user.has_group('granting.access_granting_confirm_cancel') :
                raise ValidationError(_('المبلغ لا يجب أن يكون صفر أو أقل من الصفر'))



















