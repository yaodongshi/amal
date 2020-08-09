# -*- coding: utf-8 -*-
# Copyright: giordano.ch AG

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



# add by marwa ahmed
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # override confirm function to send sale order line fields to picking lines
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        analytic_account = []
        for order in self:
            for rec in order.order_line:
                analytic_account.append(rec.sale_analytic_account_id)
            i =-1
            for line in order.picking_ids.move_ids_without_package:
                i +=1
                line.write({'analytic_account_id': analytic_account[i]})
        return result




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    sale_analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")


    # edit by marwa ahmed
    @api.onchange('product_id')
    def onchange_product_id_changes(self):
        if self.product_id:
            self.analytic_tag_ids = self.product_id.gio_analytic_tag
            self.sale_analytic_account_id = self.product_id.gio_analytic_account



    #  add by marwa ahmed
    # override function to send data from sale order line to invoice line on create inv
    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
                    'analytic_account_id': self.sale_analytic_account_id.id,
                      })

        return res

    # # override function to send data from sale order line to picking line on create inv
    # def _prepare_procurement_values(self, group_id=False):
    #     print("ppppppppppppppppppppppppppppppp")
    #     res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
    #     res.update({'analytic_account_id': self.sale_analytic_account_id.id})
    #     return res



# add by marwa ahmed
# picking lines
class StockMovee(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id')
    def onchange_stock_moves_product_id(self):
        if self.product_id:
            self.analytic_account_id = self.product_id.gio_analytic_account







