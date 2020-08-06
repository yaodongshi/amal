# -*- coding: utf-8 -*-
# Copyright: giordano.ch AG

from odoo import models, fields, api

class Purchase(models.Model):
    _inherit = 'purchase.order.line'


    @api.onchange('product_id')
    def onchange_product_id_changes(self):
        if self.product_id:
            self.analytic_tag_ids = self.product_id.gio_analytic_tag
            self.account_analytic_id = self.product_id.gio_analytic_account

# add by marwa ahmed
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    # override confirm function to send purchase order line fields to picking lines
    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        analytic_account = []
        for order in self:
            for rec in order.order_line:
                analytic_account.append(rec.account_analytic_id)
            i = -1
            for line in order.picking_ids.move_ids_without_package:
                i += 1
                line.write({'analytic_account_id': analytic_account[i]})
        return result

