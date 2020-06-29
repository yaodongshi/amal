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


class ProductTemplate(models.Model):
    _inherit = ['product.template']
    _order = "sequence, name"

    # 当内部类型变化时，改变产品的各默认值
    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.type = self.categ_id.get_cat_default('type')
            self.rental = self.categ_id.get_cat_default('rental')
            self.sale_ok = self.categ_id.get_cat_default('sale_ok')
            self.purchase_ok = self.categ_id.get_cat_default('purchase_ok')
            self.tracking = self.categ_id.get_cat_default('tracking')
