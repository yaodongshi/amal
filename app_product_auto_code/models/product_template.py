# -*- coding: utf-8 -*-

# Created on 2018-10-30
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/
# description:

from odoo import api, fields, models, exceptions, _

import itertools

class ProductTemplate(models.Model):
    _inherit = ['product.template']
    _order = "sequence, name"

    default_code = fields.Char(
        'Internal Reference',
        # compute='_compute_default_code',
        inverse='_set_code',
        store=True, default=lambda self: _('New'), copy=False)
    # 因为 default_code 有odoo的处理方式，影响面大，故会将其另存到 default_code_variant
    default_code_variant = fields.Char('Reference Prefix', inverse='_set_code_variant', copy=False)
    # 停用
    variant_max = fields.Integer('Variant Index Max', default=0)

    # odoo13 变体处理逻辑
    # attribute_line_ids 字段处理变体属性管理，管理型字段，由于存在可自定义的属性值，故不可判定有多少变体
    # product_variant_ids 处理具体的变体sku列表，是 o2m，在12中是没有这个处理的
    # 变体的处理统一放到事件 _create_variant_ids
    # 不用此方法，因为一次变更可能会执行多次，影响资源
    # 第一次执行，将现有的write active，将没有的创建
    # 第二次执行，将全部的 active
    # end _create_variant_ids
    # 创建：当spu只创建1个sku属性时，只在原sku上更新。当有了1个sku属性，再创建时，会增加。
    # 更新：
    # 删除：删除全部属性时，会删除所有sku，但第一个sku只是变成 un active。
    # 全删除属性时，sku全删除

    # 检查数据，要保证数据唯一性
    _sql_constraints = [
        ('uniq_default_code',
         'unique(default_code)',
         'The reference must be unique. Try save again.'),
    ]

    @api.model
    def create(self, vals):
        if 'categ_id' not in vals:
            vals['categ_id'] = self._get_default_category_id()
        cat = None
        if 'categ_id' in vals:
            cat = self.env['product.category'].search([('id', '=', vals['categ_id'])], limit=1)

        # 当从sku界面创建时
        if "create_product_product" in self._context:
            pass

        if 'default_code' not in vals or vals['default_code'] == _('New'):
            sequence = self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)
            if cat and cat.product_sequence:
                sequence = cat.product_sequence
            try:
                vals['default_code'] = sequence.next_by_id()
            except:
                pass
        else:
            pass
        return super(ProductTemplate, self).create(vals)

    # 处理手工改值
    def _set_code(self):
        for p in self:
            if p.default_code and p.default_code_variant != p.default_code:
                p.default_code_variant = p.default_code
            if len(p.product_variant_ids) == 1:
                p.product_variant_ids.default_code = p.default_code

    def _set_code_variant(self):
        for p in self:
            if p.default_code_variant and p.default_code != p.default_code_variant:
                p.default_code = p.default_code_variant

    # 处理变体编号，暂时用不到，都在 product 的 create 里处理
    def _reset_variant_code(self):
        for p in self:
            if p.product_variant_count > 1 and p.product_variant_ids:
                if p.default_code_variant:
                    pp_index = 1
                    for pp in p.product_variant_ids:
                        pp.write({
                            'default_code': '%s#%03d' % (p.default_code_variant, pp_index),
                        })
                        pp_index = pp_index + 1

    # 不用此方法了
    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        for p in (self):
            if p.default_code_variant and not p.default_code:
                p.default_code = p.default_code_variant

