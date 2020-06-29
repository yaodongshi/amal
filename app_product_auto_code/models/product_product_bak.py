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
        # 如果有 spu ，按 spu 排序便于处理
        try:
            vals_list = sorted(vals_list, key=lambda x: x['product_tmpl_id'])
        except:
            pass
        index_max = 0
        list_len = len(vals_list)
        old_pt = False
        # begin 只处理有1个 spu 参数
        # 处理多个 spu 值同时存在的情况，除了导入，极少
        for vals in vals_list:
            # todo: but 先建空白产品后，编辑2个以上变体，序号会少个 -1
            # code_index: 当没有变体时，值为0，有变体时，为该变体序号
            # begin 确定取序号规则与当前 spu 最大 index
            if 'product_tmpl_id' in vals:
                if not old_pt == vals['product_tmpl_id']:
                    index_max = 0
                    template = self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])], limit=1)
                    cat = template.categ_id
                    # 按产品创建产品
                    # 先取前缀 code_variant
                    # 因为 default_code 有odoo的处理方式，影响面大，故会将其另存到 default_code_variant
                    if template.default_code_variant and template.default_code_variant != '':
                        code_variant = template.default_code_variant
                    elif template.default_code and template.default_code != '':
                        code_variant = template.default_code
                    else:
                        sequence = self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)
                        if cat and cat.product_sequence:
                            sequence = cat.product_sequence
                        try:
                            code_variant = sequence.next_by_id()
                        except:
                            pass

                    sku_len = len(template.product_variant_ids)
                    # 找到最大的序号 index_max，注意要去包含 active=false 的
                    if template.product_variant_ids:
                        variant_max = max(template.with_context(active_test=False).product_variant_ids, key=lambda x: x['variant_index'])
                        try:
                            index_max = variant_max['variant_index']
                        except:
                            index_max = 0
                    code_index = index_max
                    old_pt = vals['product_tmpl_id']
                if not cat:
                    if 'categ_id' not in vals:
                        vals['categ_id'] = self._get_default_category_id()
                    cat = self.env['product.category'].search([('id', '=', vals['categ_id'])], limit=1)
            # end 确定规则与当前最大 index
            # begin 处理产品编码
            if 'product_tmpl_id' not in vals:
                # 从sku中创建
                if 'default_code' in vals and vals['default_code'] != _('New'):
                    # 有定义 default_code
                    pass
                else:
                    # 默认使用普通品的编码
                    sequence = self.env.ref('app_product_auto_code.seq_product_default', raise_if_not_found=False)
                    if cat and cat.product_sequence:
                        sequence = cat.product_sequence
                    try:
                        vals['default_code'] = sequence.next_by_id()
                    except:
                        pass
            else:
                # 从spu中创建，注意一定先创建spu，再创建其属性及相关sku
                # 有多种情况
                try:
                    attr = vals['product_template_attribute_value_ids'][0][2]
                except:
                    attr = False

                # if self.env.context.get('create_from_tmpl') and not(attr): 此条件已限制，不让在template中先直接创建变体，要求先保存
                if list_len == 1 and not (attr):
                    # 从产品创建的第一个sku产品，不带属性
                    # 没有属性值，则是单属性产品。attribute_value_ids格式为[6,0,[]]。多属性时，attribute_value_ids格式为[6,0,[x]]
                    code_index = 0
                    vals['variant_index'] = code_index
                    vals['default_code'] = code_variant
                elif list_len == 1 and attr and sku_len == 0:
                    # 有属性值了，自己是第一个属性，虽然只有1个sku，但要加上 #001
                    code_index = 1
                    vals['variant_index'] = code_index
                    vals['default_code'] = code_variant + '#%03d' % (code_index)
                elif list_len == 1 and attr and sku_len == 1:
                    # 已存在1个，当存在的1个有属性时，要改已存在的product值
                    code_index = index_max + 1
                    template.product_variant_ids[:1].variant_index = code_index
                    template.product_variant_ids[:1].default_code = code_variant + '#%03d' % (code_index)
                    # 接着改当前操作的product值
                    code_index = code_index + 1
                    vals['variant_index'] = code_index
                    vals['default_code'] = code_variant + '#%03d' % (code_index)
                elif list_len > 1:
                    code_index = code_index + 1
                    vals['variant_index'] = code_index
                    vals['default_code'] = code_variant + '#%03d' % (code_index)
                else:
                    # 当按模板
                    # 此条件常规不出现，但特殊项目会有
                    code_index = index_max + 1
                    vals['variant_index'] = code_index
                    vals['default_code'] = code_variant + '#%03d' % (code_index)

            # 自动条码处理
            if cat and cat.barcode_auto and vals['default_code']:
                vals['barcode'] = vals['default_code']
        return super(ProductProduct, self).create(vals_list)
