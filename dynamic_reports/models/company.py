# -*- coding: utf-8 -*-

from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    header = fields.Binary(string="Header", )
    header_filename = fields.Char(string="Header Filename", required=False, )
    footer = fields.Binary(string="Footer", )
    footer_filename = fields.Char(string="Footer Filename", required=False, )
    stamp = fields.Binary(string="Stamp", )
    stamp_filename = fields.Char(string="Stamp Filename", required=False)

    select_condition = fields.Selection(
        [
            ('company', 'Company Teams & Condition'),
            ('sale', 'Sale Teams & Condition'),
            ('purchase', 'Purchase Teams & Condition'),
            ('invoice', 'Invoice Teams & Condition'),
        ], string="Terms and Condition")
    terms_conditions_ar = fields.Html(string="Terms and Conditions (AR)")
    terms_conditions_en = fields.Html(string="Terms and Conditions (EN)")
    purchase_terms_conditions_ar = fields.Html(string="Terms and Conditions (AR)")
    purchase_terms_conditions_en = fields.Html(string="Terms and Conditions (EN)")
    invoice_terms_conditions_ar = fields.Html(string="Terms and Conditions (AR)")
    invoice_terms_conditions_en = fields.Html(string="Terms and Conditions (EN)")
    company_terms_conditions_ar = fields.Html(string="Terms and Conditions (AR)")
    company_terms_conditions_en = fields.Html(string="Terms and Conditions (EN)")

    ar_company_name = fields.Char()
    ar_company_street = fields.Char()

    attachment = fields.Binary("Upload Attachment",
                                 attachment=True,
                                 help="This field upload the attachment for" +
                                      "the watermark, limited to 256x256")
    attachment_alignment = fields.Boolean(string='Rotate')
    watermark = fields.Boolean(string='Watermark')
    watermark_option = fields.Selection([
        ('logo', 'Company Logo'),
        ('watermark', 'Watermark'),
        ('backgroundimage', 'Background Image'
         )],
        default='logo', string="Watermark " +
                               "Option")
    watermark_text = fields.Char(string='Watermark Text')
    alignment_angle = fields.Char(string='Alignment Angle')
    font_size = fields.Char(string='Font Size', default=20)
    font_color = fields.Char(string="Font Color")


class Partner(models.Model):
    _inherit = 'res.partner'

    ar_partner_name = fields.Char(required=False)
    ar_partner_street = fields.Char(required=False)
    customer_department_id = fields.Many2one('hr.department', string="Department", help='Department of the customer')

