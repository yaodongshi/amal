from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    contract_id = fields.Many2one('purchase.contract', string="Purchase Contract", readonly=True,
                                  states={'draft': [('readonly', False)]})
    purchase_contract_id_line = fields.Many2one('purchase.contract.line', string="Purchase Contract Line",
                                                readonly=True,
                                                states={'draft': [('readonly', False)]})

    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        for rec in self:
            res['context']['default_contract_id'] = rec.contract_id.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    contract_id = fields.Many2one('purchase.contract', string="Purchase Contract", readonly=True,
                                  states={'draft': [('readonly', False)]})
    purchase_contract_id_line = fields.Many2one('purchase.contract.line', string="Purchase Contract Line",
                                                readonly=True,
                                                states={'draft': [('readonly', False)]})
