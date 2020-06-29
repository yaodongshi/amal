# -*- coding: utf-8 -*-

# Created on 2019-01-04
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo12在线用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.sunpop.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/

{
    'name': 'Product Auto Value Auto Default by Category',
    'summary': """
    Product quick Auto value. Auto default value. Product Category Unique code.
    Product rule by category.
    """,
    "version": '13.20.03.23',
    'category': 'Sales',
    'author': 'Sunpop.cn',
    'website': 'https://www.sunpop.cn',
    'license': 'AGPL-3',
    'sequence': 2,
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
    'currency': 'EUR',
    'price': 38,
    'description': """
        Best Product Auto default value.
        Support Product with or without Variants.
        1. Add code for every Product category.产品目录编码。
        2. Quick product default value for every category. 按指定目录生成指定产品默认值。
        3. Auto setup product attribute lik Sale/Purchase, Stockable/Consumable/Service. 自动设置产品各种属性。
        4. Category can set display order. 可设置目录的排序。
        5. Drag to sort the Product sku show order. 产品可拖拽设置排序
        6. Input category code to search category in many2one select list. 在产品目录下拉选择中输入唯一编码定位相应的产品目录
        7. Add 'show_cat_name_short' in context to show short name of category. 在context中加入'show_cat_name_short'即可只显示目录短名称
        8. Multi language support.多语种支持。
    """,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'depends': [
        'stock',
        # 'sale',
        # 'purchase',
        # 'mrp',
                ],
    'data': [
        # 视图
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'data/ir_sequence_data.xml',
        'data/product_category_data.xml',
    ],
    'demo': [
    ],
}
