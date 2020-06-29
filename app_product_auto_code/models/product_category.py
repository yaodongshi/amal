# -*- coding: utf-8 -*-

# Created on 2017-11-28
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Odoo在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/
# description:

from odoo.osv import expression
from odoo import api, fields, models, exceptions, _

class ProductCategory(models.Model):
    _inherit = 'product.category'
    _order = 'sequence, ref'

    # 设置的当前目录用的 seq
    product_sequence_cur = fields.Many2one(
        'ir.sequence', 'Product Sequence',
        auto_join=True, domain="[('code', 'ilike', 'product.template')]")
    # 计算出来的 seq，当没有时自动使用上级的
    product_sequence = fields.Many2one(
        'ir.sequence', 'Product Sequence actual',
        compute='_compute_product_sequence',
        store=True,
        readonly=True)
    sequence_prefix = fields.Char('Sequence Prefix', related='product_sequence.prefix', readonly=True, store=False)

    barcode_auto = fields.Boolean('Default Barcode=Ref', default=True)

    @api.depends('product_sequence_cur', 'parent_id.product_sequence')
    def _compute_product_sequence(self):
        for rec in self:
            if rec.product_sequence_cur:
                rec.product_sequence = rec.product_sequence_cur
            elif rec.parent_id:
                rec.product_sequence = rec.parent_id.product_sequence \
                    if rec.parent_id.product_sequence else self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)
            else:
                rec.product_sequence = self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)

    # 当上级类别变化时，改变当前值
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.barcode_auto = self.parent_id.barcode_auto
            self.product_sequence_cur = self.parent_id.product_sequence_cur

        super(ProductCategory, self)._onchange_parent_id()

    @api.model
    def get_sequence(self):
        sequence = self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)
        if self.product_sequence:
            sequence = self.product_sequence
        return sequence
