# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = "Display Purchase Order Form View"

    order_id = fields.Many2one(
        'sale.order', string='Sales Order', readonly=True)

    @api.onchange('company_id', 'partner_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            for line in self.order_line:
                line.price_unit = False
                for seller in line.product_id.seller_ids:
                    if self.partner_id.id == seller.name.id and line.currency_id.id == seller.currency_id.id:
                        line._onchange_quantity()
        return res

    @api.model
    def default_get(self, default_fields):
        if "active_model" in self._context and self._context.get('active_model') == 'sale.order':
            order = self.env['sale.order'].browse(self._context['active_id'])
            order_lines = []
            for order_line in order.order_line:
                order_lines.append([0, 0, {
                    'product_id': order_line.product_id.id,
                    'name': order_line.name,
                    'date_planned': datetime.now(),
                    'product_qty': order_line.product_uom_qty,
                    'price_unit': order_line.price_unit,
                    'product_uom': order_line.product_uom.id,
                    'currency_id': order.currency_id.id,
                    'sale_line_id': order_line.id,
                    'taxes_id': order_line.tax_id}])
            contextual_self = self.with_context({
                'default_origin': order.name,
                'default_order_id': order.id,
                'default_order_line': order_lines
            })
            return super(PurchaseOrder, contextual_self).default_get(default_fields)
        return super(PurchaseOrder, self).default_get(default_fields)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = "Display Purchase Quantity"

    sale_line_id = fields.Many2one('sale.order.line', string="Sale Line")
