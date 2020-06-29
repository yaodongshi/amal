# -*- coding: utf-8 -*-
from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Count the Purchase Orders"

    def purchase_order_count(self):
        self.order_count = self.env['purchase.order'].search_count(
            [('order_id', 'in', self.ids)])

    order_count = fields.Integer(compute='purchase_order_count')

    def action_purchase_order(self):
        [action] = self.env.ref('purchase.purchase_order_tree').read()
        action['domain'] = [('order_id', 'in', self.ids)]
        return action


class CountPurchaseOrder(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    @api.depends('purchase_line_ids.product_qty', 'purchase_line_ids.product_uom', 'purchase_line_ids.order_id.state')
    def _get_purchase_qty(self):
        for line in self:
            purchase_qty = 0.0
            for purchase_line in line.purchase_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id):
                if purchase_line.order_id.state not in ['draft', 'cancel']:
                    purchase_qty += purchase_line.product_uom._compute_quantity(purchase_line.product_qty, line.product_uom)
            line.qty_purchase = purchase_qty

    qty_purchase = fields.Float('Purchase Quantity', default=0.0, compute='_get_purchase_qty', store=True)
    purchase_line_ids = fields.One2many('purchase.order.line', 'sale_line_id', string='PurchaseLine')
