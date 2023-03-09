# -*- coding: utf-8 -*-

from odoo import models, fields, api
import qrcode
import binascii
import base64
from io import BytesIO
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.safe_eval import pytz


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    qr_code = fields.Binary(string="QR Code", compute="_generate_qr_code_e_sale")
    sale_terms_conditions_ar = fields.Html(string='Sale Terms Conditions', translate=True)
    sale_terms_conditions_en = fields.Html(string='Sale Terms Conditions', translate=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for rec in self:
            rec.sale_terms_conditions_ar = rec.company_id.terms_conditions_ar
            rec.sale_terms_conditions_en = rec.company_id.terms_conditions_en

    def _string_to_hex(self, value):
        if value:
            string = str(value)
            string_bytes = string.encode("UTF-8")
            encoded_hex_value = binascii.hexlify(string_bytes)
            hex_value = encoded_hex_value.decode("UTF-8")
            return hex_value

    def _get_hexa(self, tag, length, value):
        if tag and length and value:
            hexa_str = self._string_to_hex(value)
            length = int(len(hexa_str) / 2)
            conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
            hexa_decimal = ''
            while (length > 0):
                remainder_val = length % 16
                hexa_decimal = conversion_table[remainder_val] + hexa_decimal
                length = length // 16
            if len(hexa_decimal) == 1:
                hexa_decimal = "0" + hexa_decimal
            return tag + hexa_decimal + hexa_str

    def get_qr_code_vals(self):
        if not self.company_id.vat:
            raise UserError('Missing VAT Number for the company')
        elif not self.partner_id.vat:
                raise UserError('Missing VAT Number for the customer')
        customer_name = str(self.partner_id.name)
        customer_vat_no = str(self.partner_id.vat)
        enypt_customer_name = self._get_hexa("01", "0c", customer_name)
        enypt_customer_vat_no = self._get_hexa("02", "0f", customer_vat_no)
        self_user = self.env.user
        if self.env.user.tz:
            date_time_now = self.date_order
            date_order = date_time_now.strftime("%Y-%m-%dT%H:%M:%S")
            date_order_x = datetime.strptime(date_order, "%Y-%m-%dT%H:%M:%S")
            date_order_time = date_order_x.astimezone(pytz.timezone(self.env.user.tz)).isoformat()
            date_order_time = date_order_time.split('+')[0] + 'Z'
        else:
            raise UserError('User Time Zone is Missing. Please Add Timezone for the User..')

        enypt_date = self._get_hexa("03", "14", date_order_time)
        enypt_amount_total_with_vat = self._get_hexa("04", "0a", str(round(self.amount_total, 2)))
        enypt_amount_vat = self._get_hexa("05", "09", str(round(self.amount_tax, 2)))

        enypt_qr = enypt_customer_name + enypt_customer_vat_no + enypt_date + enypt_amount_total_with_vat + enypt_amount_vat
        encoded_base64_bytes = base64.b64encode(bytes.fromhex(enypt_qr)).decode()
        return encoded_base64_bytes

    def _generate_qr_code_e_sale(self):
        qr_code = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_code.add_data(self.get_qr_code_vals())
        qr_code.make(fit=True)
        img = qr_code.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
