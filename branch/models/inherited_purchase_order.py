# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare



class purchase_order(models.Model):
    _inherit = 'purchase.order.line'

    # @api.multi
    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id or False
        return branch_id

    branch_id = fields.Many2one('res.branch', related='order_id.branch_id', default=_default_branch_id)

    # @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                val.update({
                    'branch_id': line.branch_id.id,
                })

                done += moves.create(val)
        return done

    def _prepare_account_move_line(self, move):
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        return {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'purchase_line_id': self.id,
            'date_maturity': move.invoice_date_due,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'partner_id': move.partner_id.id,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'display_type': self.display_type,
            'branch_id': self.order_id.branch_id.id,

        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # @api.multi
    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrder, self).default_get(fields)
        user_branch = self.env['res.users'].browse(self.env.uid).branch_id
        if user_branch:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', user_branch.id)])
            if branched_warehouse:
                res['picking_type_id'] = branched_warehouse[0].in_type_id.id
            else:
                res['picking_type_id'] = False
        else:
            res['picking_type_id'] = False
        return res

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res['branch_id'] = self.branch_id.id
        return res

    # @api.multi
    # def action_view_invoice(self):
    #     print("action_view_invoice")
    #     '''
    #     This function returns an action that display existing vendor bills of given purchase order ids.
    #     When only one found, show the vendor bill immediately.
    #     '''
    #     action = self.env.ref('account.action_move_in_invoice_type')
    #     result = action.read()[0]
    #     create_bill = self.env.context.get('create_bill', False)
    #     # override the context to get rid of the default filtering
    #     result['context'] = {
    #         'type': 'in_invoice',
    #         'default_purchase_id': self.id,
    #         'default_currency_id': self.currency_id.id,
    #         'default_company_id': self.company_id.id,
    #         'company_id': self.company_id.id,
    #         'branch_id': self.branch_id.id,
    #     }
    #     # choose the view_mode accordingly
    #     if len(self.invoice_ids) > 1 and not create_bill:
    #         result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
    #     else:
    #         res = self.env.ref('account.view_move_form', False)
    #         result['views'] = [(res and res.id or False, 'form')]
    #         # Do not set an invoice_id if we want to create a new bill.
    #         if not create_bill:
    #             result['res_id'] = self.invoice_ids.id or False
    #     return result

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'branch_id': self.branch_id.id,

        }

        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view

            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_origin'] = self.name
        result['context']['default_reference'] = self.partner_ref
        return result
