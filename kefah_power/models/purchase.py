# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sa_vat = fields.Char(string="VAT", related='partner_id.vat')

    @api.constrains('partner_id')
    def _check_partner_vat(self):
        for rec in self:
            if not rec.sa_vat:
                raise UserError(_('%s Vendor Vat Id is missing!') % self.partner_id.name)
