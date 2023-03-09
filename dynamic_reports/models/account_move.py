# -*- coding: utf-8 -*-

from odoo import fields, models
import qrcode
import binascii
import base64
from io import BytesIO
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.safe_eval import pytz


class AccountMove(models.Model):
    _inherit = 'account.move'

    qr_code = fields.Binary(string="QR Code", compute="_generate_qr_code_e_invoice")
    invoice_terms_conditions_ar = fields.Html(string="Terms and Conditions (AR)", track_visibility='onchange')
    invoice_terms_conditions_en = fields.Html(string="Terms and Conditions (EN)", track_visibility='onchange')
    po_no = fields.Char(string="PO NO")
    invoice_data_time = fields.Datetime(string='Invoice Date Time', readonly=True, default=fields.Datetime.now)

    def action_post(self):
        # inherit of the function from account.move to validate a new invoice_data_time of a invoice
        self.invoice_data_time = datetime.now()
        res = super(AccountMove, self).action_post()

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
        if self.move_type in ('in_invoice', 'in_refund'):
            if not self.partner_id.vat:
                raise UserError('Missing VAT Number for the vendor')
            partner = str(self.partner_id.name)
            partner_vat_no = self.partner_id.vat

        else:
            if not self.company_id.vat:
                raise UserError('Missing VAT Number for the customer')
            partner = str(self.company_id.name)
            partner_vat_no = self.company_id.vat or ''
            if self.partner_id.company_type == 'company':
                partner_name = self.partner_id.name
                partner_vat = self.partner_id.vat
        partner_hex = self._get_hexa("01", "0c", partner)
        partner_vat_hex = self._get_hexa("02", "0f", partner_vat_no)
        self_user = self.env.user
        if self.env.user.tz:
            # date_time_now = self.invoice_date
            date_time_now = self.invoice_data_time
            general_invoice_date = date_time_now.strftime("%Y-%m-%dT%H:%M:%S")
            general_invoice_date1 = datetime.strptime(general_invoice_date, "%Y-%m-%dT%H:%M:%S")
            invoice_date_time = general_invoice_date1.astimezone(pytz.timezone(self.env.user.tz)).isoformat()
            invoice_date_time = invoice_date_time.split('+')[0] + 'Z'
        else:
            raise UserError('Time Zone is Missing!!! Please Set Timezone for the User..')
        date_hexa = self._get_hexa("03", "14", invoice_date_time)
        amount_total_with_vat_hex = self._get_hexa("04", "0a", str(round(self.amount_total, 2)))
        amount_vat_hex = self._get_hexa("05", "09", str(round(self.amount_tax, 2)))

        qr_hex = partner_hex + partner_vat_hex + date_hexa + amount_total_with_vat_hex + amount_vat_hex
        encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
        return encoded_base64_bytes

    def _generate_qr_code_e_invoice(self):
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