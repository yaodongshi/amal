# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _inherit = 'sale.order'

    adv_payment_ids = fields.Many2many('account.payment', string="Advance Payment", copy=False)

    def action_view_adv_payments(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        action['domain'] = [('id', 'in', self.adv_payment_ids.ids)] if self.adv_payment_ids.ids else []
        action['context'] = {'create': 0}
        return action

    def btn_advance_payment(self):
        cus_ctx = {'default_payment_type': 'inbound',
                   'default_partner_type': 'customer',
                   'search_default_inbound_filter': 1,
                   'res_partner_search_mode': 'customer',
                   'default_partner_id': self.partner_id.id,
                   'default_communication': self.name,
                   'active_ids':[],
                   'active_model':self._name,
                   'active_id':self.id,
                   'default_currency_id': self.currency_id.id}
        ctx = self._context.copy()
        ctx.update(cus_ctx)
        return {
            'name': _('Advance Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('eq_sale_advance_payment.view_sale_advance_account_payment_form').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': ctx
        }

class account_payment(models.Model):
    _inherit = 'account.payment'

    create_in_state_sale = fields.Selection([('draft', 'Draft'),
                                             ('confirm', 'Confirm')],
                                            default='confirm',
                                            string="Payment Status")

    def create_sale_adv_payment(self):
        if self.amount <= 0.0:
            raise ValidationError(_("The payment amount cannot be negative or zero."))
        if self.create_in_state_sale == 'confirm':
            self.post()
        if self.env.context.get('active_id'):
            sale_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
            sale_id.write({'adv_payment_ids': [(4, self.id)]})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
