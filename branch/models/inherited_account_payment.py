# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        rec = super(AccountPayment, self)._get_move_vals(journal)
        if self.branch_id:
            rec['branch_id'] = self.branch_id.id
        print('ssss', rec)
        return rec

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        rec = super(AccountPayment, self)._get_shared_move_line_vals( debit, credit, amount_currency, move_id, invoice_id=False)
        if self.branch_id:
            rec['branch_id']=self.branch_id.id
        print('ssss',rec)
        return rec


    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:

            invoice = invoice_defaults[0]
            print(' invoice.get', invoice.get('branch_id'))

            rec['communication'] = invoice['ref'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['amount_residual']
            rec['branch_id'] = invoice.get('branch_id') and invoice.get('branch_id')[0]
        return rec

    branch_id = fields.Many2one('res.branch')
    #
    # @api.multi
    # def _default_branch_id(self):
    #     print ("sssssssssssssssssssssssssssssssssssssssssssss",self._context.get('branch_id'))
    #     if not self._context.get('branch_id'):
    #        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
    #     else:
    #        branch_id =  self._context.get('branch_id')
    #     return branch_id
    #
    # branch_id = fields.Many2one('res.branch', default=_default_branch_id)

