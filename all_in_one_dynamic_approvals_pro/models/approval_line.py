# -*- coding: utf-8 -*-
#####################################################################################
   #
   # Keffah Solutions the Est. Information technology and Communication  Pvt. Ltd.
   #
   # Copyright (C) 2021-TODAY Keffah Solutions the Est. Information technology and Communication Pvt. Ltd
   # (<https://www.kascco.sa>).
   # Author: Keffah Solutions the Est. Information technology and Communication Pvt. Ltd (Contact : itcs@kascco.sa)
   #
   # This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
   # It is forbidden to publish, distribute, sublicense, or sell copies of the Software
   # or modified copies of the Software.
   #
   # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
   # IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
   # DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
   # ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
   # DEALINGS IN THE SOFTWARE.

#######################################################################################

from odoo import models, fields


class ApprovalLine(models.Model):
    _name = 'approval.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Approval Order Line'

    sequence = fields.Integer(string='Approver Sequence')
    approval_id = fields.Many2one('dynamic.approval')
    approver_id = fields.Many2one('res.users', string='Approver')
    reject_reason = fields.Text(string='Reject Reason')
    time_limit = fields.Integer(string="Approver Time Limit ")
    delay = fields.Boolean(string="Approval Delayed",
                           help="The approver given time limit is crossed. "
                                "The approval is esculated to the authority")
    authority_email_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Email Sent')],
        string="Authority Email Status", readonly=False, default='draft', tracking=True)
    is_send = fields.Boolean(string="Is send",
                           help="Check the approval requested person delay info mail sent or not")
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    approval_duration = fields.Char(string='Approval Duration')
    approval_email_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Email Sent')],
        string="Email Status", readonly=False, default='draft', tracking=True)
    approval_status = fields.Selection([
        ('approve', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Reject')],
        string="Status", readonly=False, default='draft', tracking=True)
