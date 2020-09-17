# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class ShipCostLine(models.Model):
    _name = 'ship.cost.line'
    _description = 'Purchase Contract Lines'
    _rec_name = 'name'
    _order = 'name DESC'

    name = fields.Char(string="Description", required=True, copy=False)
    contract_id = fields.Many2one('purchase.contract', string="Purchase Contract")
    purchase_contract_line_id = fields.Many2one('purchase.contract.line', string="Purchase Contract Line")
    freight = fields.Float("Freight")
    thc = fields.Float("THC")
    currency_id = fields.Many2one('res.currency', string="Currency")
