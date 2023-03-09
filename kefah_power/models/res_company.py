# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = 'res.company'

    is_man_power = fields.Boolean(string="Is Man Power?", )

