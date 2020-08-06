# -*- coding: utf-8 -*-
# Copyright: giordano.ch AG

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"


    gio_analytic_account = fields.Many2one('account.analytic.account', string="ANALYTIC ACCOUNT")
    gio_analytic_tag = fields.Many2one('account.analytic.tag', string="ANALYTIC TAG", copy=False)

    # added by doaa
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        name = res.name
        default_code = res.default_code
        analytic_name = str(default_code) + '/' + name
        res.gio_analytic_account = self.env['account.analytic.account'].create({'name': analytic_name}).id
        return res

    # added by doaa
    def write(self, vals):
        if 'name' in vals and 'default_code' not in vals:
            name = vals['name']
            default_code = self.default_code
            analytic_name = default_code + '/' + name
            if self.gio_analytic_account:
               self.gio_analytic_account.name = analytic_name
            else:
                self.gio_analytic_account = self.env['account.analytic.account'].create({'name': analytic_name}).id

        if 'name' not in vals and 'default_code' in vals:
            name = self.name
            default_code = vals['default_code']
            analytic_name = default_code + '/' + name
            if self.gio_analytic_account:
               self.gio_analytic_account.name = analytic_name
            else:
                self.gio_analytic_account = self.env['account.analytic.account'].create({'name': analytic_name}).id
        if 'name' in vals and 'default_code' in vals:
            name = vals['name']
            default_code = vals['default_code']
            analytic_name = default_code + '/' + name
            if self.gio_analytic_account:
               self.gio_analytic_account.name = analytic_name
            else:
                self.gio_analytic_account = self.env['account.analytic.account'].create({'name': analytic_name}).id
        return super(ProductTemplate, self).write(vals)
