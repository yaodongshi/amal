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

    # todo: 重构默认值生成办法，app_default_[field_name]，做个通用方法
    app_default_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Stockable Product')], string='Default Product Type', default='product',
        help='Product in this category would set default type to this value.')

    app_default_sale_ok = fields.Boolean(
        'Default Can be Sold', default=True,
        help="Specify if the product can be selected in a sales order line.")
    app_default_purchase_ok = fields.Boolean('Default Can be Purchased', default=True)
    app_default_rental = fields.Boolean('Default Can be Rent')
    app_default_tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Default Tracking", default='none')

    ref = fields.Char('Unique Code', index=True, copy=False)
    sequence = fields.Integer('Sequence', default=10, help="Determine the display order")

    # 增加目录编号唯一检查
    _sql_constraints = [
        ('uniq_ref',
         'unique(ref)',
         'The reference must be unique'),
    ]

    # 产品目录序号器，产生默认值，或者手工录入
    @api.model
    def default_get(self, fields):
        res = super(ProductCategory, self).default_get(fields)
        if 'ref' in res and res.ref != _('New'):
            pass
        else:
            try:
                res.update({'ref': self.env['ir.sequence'].next_by_code('product.category.default')})
            except Exception as e:
                pass
        return res

    @api.model
    def get_cat_default(self, field):
        # 暂时不处理向上遍历取，因为 bool 不好处理。
        # todo:  bool 类型字段特殊处理
        if hasattr(self, 'app_default_%s' % (field)):
            return self['app_default_%s' % (field)]
        else:
            return False

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        # 处理可以按ref和名称搜索
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('ref', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]

        ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(ids).name_get()

    # 当上级类别变化时，改变当前值，只要该列名定义为 app_default_ 开头
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            f_set = []
            for f in self._fields.keys():
                if 'app_default_' in f:
                    f_set.append(f)
                    self[f] = self.parent_id[f]

    # 当传参 show_cat_name_short 时，只显示短目录名
    def name_get(self):
        try:
            if self._context.get('show_cat_name_short'):
                return [(value.id, "%s" % (value.name)) for value in self]
            else:
                return [(value.id, "%s" % (value.complete_name)) for value in self]
        except:
            return super(ProductCategory, self).name_get()

