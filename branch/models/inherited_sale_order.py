# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        return {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'branch_id': self.order_id.branch_id.id

        }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.multi
    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id or False
        return branch_id

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        user_branch = self.env['res.users'].browse(self.env.uid).branch_id
        if user_branch:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', user_branch.id)])
            if branched_warehouse:
                res['warehouse_id'] = branched_warehouse.ids[0]
            else:
                res['warehouse_id'] = False

        return res

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

    # @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res
