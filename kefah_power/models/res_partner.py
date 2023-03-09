# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(index=True)
    sa_vat = fields.Char(string="VAT", related='vat')

    @api.constrains('name')
    def _check_name(self):
        partner = self.env['res.partner'].search(
            [('name', 'ilike', self.name), ('id', '!=', self.id)])
        if partner:
            raise UserError(_('The name of the partner must be unique!'))


