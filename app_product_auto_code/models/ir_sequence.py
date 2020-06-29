# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date as datetime_date
from dateutil.relativedelta import relativedelta
# import calendar


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    # 增加翻译
    name = fields.Char(required=True, translate=True)
