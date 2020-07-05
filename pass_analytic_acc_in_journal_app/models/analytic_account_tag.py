# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    add_analytic_acc_tag = fields.Boolean(string="Analytic Account & Tags")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Analytic Tags")

    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()
        tags = [tag.id for tag in self.analytic_tag_ids]
        if self.add_analytic_acc_tag:
            for move_line in res[0]['line_ids']:
                move_line[2].update({'analytic_account_id':self.analytic_account_id.id,'analytic_tag_ids':[(6,0,tags)]})   
        return res

    def post(self):
        res = super(AccountPayment, self).post()
        account_move = self.env['account.move'].browse(self._context.get('active_id'))
        tags = [tag.id for tag in self.analytic_tag_ids]
        if self.add_analytic_acc_tag:
            for invoice_line in account_move.invoice_line_ids:
                invoice_line.update({'analytic_account_id':self.analytic_account_id.id, 'analytic_tag_ids':[(6,0,tags)]})
        return res    
