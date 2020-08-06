from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot', copy=False)

    # doaa added
    @api.onchange('product_id')
    def onchange_product_id_changes_lot(self):
        if self.product_id:
            self.lot_id = self.env['stock.production.lot'].search(
                                 [('product_id', '=', self.product_id.id)], limit=1).id

    # @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res
