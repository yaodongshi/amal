from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id or False
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id or False
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        if not self.supplier_id:
            raise UserError(
                _('Enter a supplier.'))
        supplier = self.supplier_id
        data = {
            'origin': origin,
            'partner_id': self.supplier_id.id,
            'fiscal_position_id': supplier.property_account_position_id and
                                  supplier.property_account_position_id.id or False,
            'picking_type_id': picking_type.id,
            'company_id': company.id,
            'group_id': group_id.id,
            'branch_id': self.branch_id.id,
        }
        return data

