# -*- coding: utf-8 -*-
#####################################################################################

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


class ApproverLine(models.Model):
    _name = 'approver.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Approver  Line'

    sequence = fields.Integer(string='Approver Sequence', default='1')
    approver_id = fields.Many2one('dynamic.approval')
    user_ids = fields.Many2one('res.users', string='Approvers', tracking=True)
    time_limit_active = fields.Boolean(string="Manual LimitActive",
                                            related="approver_id.enable_time_limit",
                                            help="check the Manuall time limit is active or not")
    individual_time_active = fields.Boolean(string="Individual LimitActive",
                                            related="approver_id.individual_time_limit",
                                            help="check the individual time limit is active or not")
    approver_time_limit = fields.Float(string="Approver Time Limit",
                                       related="approver_id.timer",
                                       readonly=True)
    individual_time_limit = fields.Float(
        string="Approver Individual Time Limit")
