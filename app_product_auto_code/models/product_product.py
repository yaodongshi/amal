# -*- coding: utf-8 -*-

# Created on 2018-11-01
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
from odoo import models, fields, api, exceptions, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char('Internal Reference',
                               inverse='_set_code', index=True, default=lambda self: _('New'), copy=False)
    variant_index = fields.Integer('Variant Index', default=0, readonly=True, copy=False)

    # 检查数据，要保证数据唯一性
    _sql_constraints = [
        ('uniq_default_code',
         'unique(default_code)',
         'The reference must be unique. Try save again.'),
    ]

    def copy(self, default=None):
        if len(self.product_tmpl_id.product_variant_ids) > 1:
            raise exceptions.ValidationError(_('Product varient can only create in Product view!'))
        return super(ProductProduct, self).copy(default=None)

    def _set_code(self):
        for p in self:
            if p.default_code and p.categ_id.barcode_auto:
                p.barcode = p.default_code


    # todo: 多公司的处理
    @api.model_create_multi
    def create(self, vals_list):
        # 为加速大量导入。只处理不从 spu 中创建的情况
        # 从spu中创建的，在 _create_variant_ids 中处理
        # 如果有 spu ，按 spu 排序便于处理
        try:
            vals_list = sorted(vals_list, key=lambda x: x['product_tmpl_id'])
        except:
            pass
        index_max = 0
        old_spu = False
        for vals in vals_list:
            cat = False
            # todo: but 先建空白产品后，编辑2个以上变体，序号会少个 -1
            # code_index: 当没有变体时，值为0，有变体时，为该变体序号
            # begin 确定取序号规则与当前 spu 最大 index
            if 'default_code' in vals and vals['default_code'] != _('New'):
                pass
            else:
                if 'product_tmpl_id' not in vals:
                    if 'categ_id' not in vals:
                        vals['categ_id'] = self._get_default_category_id()
                    cat = self.env['product.category'].search([('id', '=', vals['categ_id'])], limit=1)
                    # 从sku中创建
                    if 'default_code' in vals and vals['default_code'] != _('New'):
                        # 有定义 default_code
                        pass
                    else:
                        # 默认使用普通品的编码
                        vals['default_code'] = cat.get_sequence().next_by_id()
                elif 'product_template_attribute_value_ids' in vals and not vals['product_template_attribute_value_ids'][0][2]:
                    # 处理从产品创建的情况，无属性产品，与spu相同
                    template = self.env['product.template'].browse(vals['product_tmpl_id'])
                    vals['default_code'] = template.default_code
                    cat = template.categ_id
                else:
                    # 处理从产品创建的情况，有属性的产品
                    # begin 取最大值 index，每换一个 spu 重置基础值
                    if old_spu != vals['product_tmpl_id']:
                        template = self.env['product.template'].browse(vals['product_tmpl_id'])
                        if template.product_variant_ids:
                            variant_max = max(template.with_context(active_test=False).product_variant_ids, key=lambda x: x['variant_index'])
                            index_max = variant_max['variant_index'] if variant_max and variant_max['variant_index'] else 0
                        else:
                            index_max = 0
                        cat = template.categ_id
                        if template.default_code_variant and template.default_code_variant != '':
                            code_variant = template.default_code_variant
                        elif template.default_code and template.default_code != '':
                            code_variant = template.default_code
                        old_spu = vals['product_tmpl_id']
                    # end 取最大值 index
                    index_max = index_max + 1
                    vals['variant_index'] = index_max
                    vals['default_code'] = code_variant + '#%03d' % (index_max)

            # 自动条码处理
            if cat and cat.barcode_auto and 'default_code' in vals and vals['default_code']:
                vals['barcode'] = vals['default_code']
        return super(ProductProduct, self).create(vals_list)
