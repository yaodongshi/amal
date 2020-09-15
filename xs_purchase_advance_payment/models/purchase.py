# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import models, fields, api, exceptions, _

class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def _get_amount(self):
        advance_amount = 0.0
        for line in self.account_payment_ids:
            if line.state != 'draft':
                advance_amount += line.amount
        self.amount_resisual = self.amount_total - advance_amount

    account_payment_ids = fields.One2many('account.payment', 'purchase_id', string="Pay Purchase Advanced")
    amount_resisual = fields.Float('Residual amount', readonly=True, compute="_get_amount")

    # doaa added
    def btn_advance_payment(self):
        date = ''
        if self.date_approve:
           date = self.date_approve
        if self.date_order:
           date = self.date_order
        ctx = {'default_payment_type': 'outbound',
               'default_partner_id': self.partner_id.id,
               'default_partner_type': 'supplier',
               'search_default_outbound_filter': 1,
               'res_partner_search_mode': 'supplier',
               'default_currency_id': self.currency_id.id,
               'default_payment_date': date,
               'default_purchase_id': self.id,
               'default_communication': self.name,
               'default_payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
               'active_ids': [],
               'active_model': self._name,
               'active_id': self.id,
               }

        return {'name': _("Advance Payment"),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'target': 'new',
                'view_id': self.env.ref('xs_purchase_advance_payment.view_purchase_advance_account_payment_form').id,
                'context': ctx}

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    create_in_state_purchase = fields.Selection([('draft', 'Draft'),
                                             ('confirm', 'Confirm')],
                                            default='confirm',
                                            string="Payment Status")

    def create_purchase_adv_payment(self):
        if self.amount <= 0.0:
            raise ValidationError(_("The payment amount cannot be negative or zero."))
        if self.create_in_state_purchase == 'confirm':
            self.post()
        if self.env.context.get('active_id'):
            purchase_id = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            purchase_id.write({'account_payment_ids': [(4, self.id)]})
        return True