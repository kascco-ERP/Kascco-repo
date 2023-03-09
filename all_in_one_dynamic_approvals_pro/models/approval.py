# -*- coding: utf-8 -*-
######################################################################################
#
#    Keffah Solutions the Est. Information technology and Communication  Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Keffah Solutions the Est. Information technology and Communication Pvt. Ltd
#    (<https://www.kascco.sa>).
#    Author: Keffah Solutions the Est. Information technology and Communication Pvt. Ltd (Contact : itcs@kascco.sa)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


def _export_xml_id(self):
    """ Return a valid xml_id for the record ``self``. """
    if not self._is_an_ordinary_table():
        raise Exception(
            "You can not export the column ID of model %s, because the "
            "table %s is not an ordinary table."
            % (self._name, self._table))
    ir_model_data = self.sudo().env['ir.model.data']
    data = ir_model_data.search([('model', '=', self._name),
                                 ('res_id', '=', self.id)])
    if data:
        if data[0].module:
            return '%s.%s' % (data[0].module, data[0].name)
        else:
            return data[0].name
    else:
        postfix = 0
        name = '%s_%s' % (self._table, self.id)
        while ir_model_data.search([('module', '=', '__export__'),
                                    ('name', '=', name)]):
            postfix += 1
            name = '%s_%s_%s' % (self._table, self.id, postfix)
        ir_model_data.create({
            'model': self._name,
            'res_id': self.id,
            'module': '__export__',
            'name': name,
        })
        return '__export__.' + name


class Approval(models.Model):
    """This class is creating the approval forms and it's functions"""
    _name = 'dynamic.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Dynamic Multi Approval'

    name = fields.Char(string='Approval Number', readonly=True,
                       required=True, copy=False, index=True, tracking=True,
                       default=lambda self: _('New'))
    approval_name = fields.Char(string="Approval Name", required=False)
    model_id = fields.Many2one('ir.model', string='Model', required=True,
                               index=True, ondelete='cascade')
    model_states = fields.Many2many('ir.model.fields.selection',
                                    string='State', required=True)
    category_id = fields.Many2one('ir.module.category', string="Category",
                                  required=True)
    action_id = fields.Many2many("ir.actions.act_window",
                                 string="Actions Window", required=True)
    company_id = fields.Many2many('res.company', string='Company',
                                  required=True)
    is_reminder = fields.Boolean(string="Reminder Mail", default=False)
    delay_time = fields.Integer(default=1, help="Check delay every x.")
    delay_type = fields.Selection([('minutes', 'Minutes'),
                                   ('hours', 'Hours'),
                                   ('days', 'Days'),
                                   ('weeks', 'Weeks'),
                                   ('months', 'Months')],
                                  string='Delay Type', default='hours')
    users = fields.One2many('approver.line', 'approver_id', string='Approvers')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('multi_state_activated', 'Multi State Activated'),
        ('old', 'Apply to Old Records'),
        ('update', 'Update'),
        ('apply', 'Approvers List Updated'),
        ('cancel', 'Refused')
    ], string='Status', index=True, readonly=True, tracking=True,
        copy=False, default='draft',
        required=True, help='Approval State')

    group_id = fields.Many2one('res.groups')
    view_id = fields.Many2one('ir.ui.view')
    remove_reports = fields.Boolean(string="Remove Reports")

    add_approval_status_to_tree = fields.Boolean(string="Add Approval Status"
                                                        " To Tree View")
    tree_view_id = fields.Many2one('ir.ui.view')
    tree_view_name = fields.Many2one('ir.ui.view')
    tree_view_inherit_id = fields.Char(string="Tree View Inherit Id",
                                       related='tree_view_name.xml_id')

    search_view_id = fields.Many2one('ir.ui.view')
    add_filter = fields.Boolean(string="Add Filter")
    search_view_name = fields.Many2one('ir.ui.view')
    search_view_inherit_id = fields.Char(string="Search View Inherit Id",
                                         related='tree_view_name.xml_id')

    enable_time_limit = fields.Boolean(string="Enable Timer",
                                       help="This will activate the Time limit for the approvers")
    timer = fields.Float(String="Time Limit")
    timer_type = fields.Selection([('hours', 'Hours')],
                                  string='Timer Type', default='hours', readonly=True)
    user_ids = fields.Many2many('res.users', string='Authority', tracking=True)
    individual_time_limit = fields.Boolean(string="Individual Time Limit",
                                           help="This will activate the Time limit can set individualy")

    custom_field_id = fields.Many2one('ir.model.fields')
    multi_state_field_id = fields.Many2one('ir.model.fields')
    fully_approved_field_id = fields.Many2one('ir.model.fields')
    need_to_approve_id = fields.Many2one('ir.model.fields')
    reminder_mail = fields.Many2one('ir.model.fields')
    parallel_approval_duration_id = fields.Many2one('ir.model.fields')
    multi_approver_status_checker_id = fields.Many2one('ir.model.fields')
    email_status_checker_id = fields.Many2one('ir.model.fields')
    check_old_records_id = fields.Many2one('ir.model.fields')
    check_approvers_list = fields.Many2one('ir.model.fields')

    approve_state_id = fields.Many2one('ir.model.fields')
    reject_reason_id = fields.Many2one('ir.model.fields')

    report_action_ids = fields.Many2many('ir.actions.report',
                                         string='Report Actions')
    automation_action_id = fields.Many2one('base.automation')
    email_template_id = fields.Many2one('mail.template')
    check_approval_delay = fields.Many2one('ir.cron')

    approve_server_action_id = fields.Many2one('ir.actions.server')
    reject_server_action_id = fields.Many2one('ir.actions.server')
    re_send_server_action_id = fields.Many2one('ir.actions.server')
    email_template_server_action_id = fields.Many2one('ir.actions.server')
    multiple_server_action_id = fields.Many2one('ir.actions.server')

    approver_ids = fields.Many2one('ir.model.fields')
    approval_model = fields.Many2one('ir.model.fields')
    approval_id = fields.Many2one('ir.model.fields')

    @api.model
    def create(self, vals):
        """"creating sequence number for Approval"""
        if vals.get('sequence', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('dynamic.approval')
            return super(Approval, self).create(vals)

    @api.onchange('approval_name')
    def filter_model(self):
        """This onchange() will filter state field contain models"""
        state_field_contain_models = self.env['ir.model.fields'].search(
            [('ttype', '=', 'selection'), ('name', '=', 'state'),
             ('selection_ids', '!=', False)]).mapped(
            'model_id').ids
        return {'domain': {'model_id': [('id', 'in', state_field_contain_models)
                                        ]}}

    @api.onchange('model_id')
    def onchange_model_id(self):
        """This Onchange function will list the selected model state values,
        action_id and tree view name"""
        states = self.model_id.field_id.filtered(
            lambda l: l.name == 'state').selection_ids.mapped('id')
        tree_view = self.model_id.view_ids.filtered(
            lambda l: l.type == 'tree')
        search_view = self.model_id.view_ids.filtered(
            lambda l: l.type == 'search')
        return {'domain': {'model_states': [('id', 'in', states)],
                           'action_id': [('res_model', '=', self.model_id.model)],
                           'tree_view_name': [('id', 'in', tree_view.ids)],
                           'search_view_name': [('id', 'in', search_view.ids)]
                           }}

    def create_button(self):
        """This function will create the approval needed field,Button functions
        and it will inherit and create new
        view in corresponding model"""
        self.write({'state': 'active'})
        xml_id = self.model_id.view_ids.filtered(
            lambda l: not l.inherit_id and l.type == 'form').xml_id
        inherit_id = self.env.ref(xml_id)
        group_obj = self.env['res.groups']
        inherit_name = inherit_id.name + ".dynamic.approval"

        approve_action_name = self.model_id.name + ' Approve Action'
        reject_action_name = self.model_id.name + ' Reject Action'
        re_send_action_name = self.model_id.name + ' Resend Action'

        if not self.custom_field_id:
            self.custom_field_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_approve',
                'field_description': 'Approve',
                'readonly': 'True',
                'model_id': self.model_id.id})
        if not self.need_to_approve_id:
            self.need_to_approve_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_need_to_approve',
                'field_description': 'Need To Approve',
                'readonly': 'True',
                'model_id': self.model_id.id})
        if not self.parallel_approval_duration_id:
            self.parallel_approval_duration_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_check_parllel_approval',
                'field_description': 'Check Parallel Approval Duration',
                'readonly': 'True',
                'model_id': self.model_id.id})
        if not self.reminder_mail:
            self.reminder_mail = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_reminder_mail',
                'field_description': 'Check Delay Mail Reminder ',
                'readonly': 'True',
                'model_id': self.model_id.id})

        if not self.approve_state_id:
            self.approve_state_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'selection',
                'name': 'x_approve_state',
                'field_description': 'Approval Status',
                'model_id': self.model_id.id})
            self.env['ir.model.fields.selection'].sudo().create([
                {'field_id': self.approve_state_id.id,
                 'value': 'approve',
                 'name': 'Waiting for Approval'},
                {'field_id': self.approve_state_id.id,
                 'value': 'approved',
                 'name': 'Approved'},
                {'field_id': self.approve_state_id.id,
                 'value': 'reject',
                 'name': 'Reject'}
            ])
        if not self.multi_state_field_id:
            self.multi_state_field_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_multi_state',
                'field_description': 'Multi State',
                'readonly': 'True',
                'model_id': self.model_id.id,
            })
        if not self.approval_id:
            self.approval_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'many2one',
                'relation': 'dynamic.approval',
                'name': 'x_approval_id',
                'field_description': 'Approval Id',
                'readonly': 'True',
                'model_id': self.model_id.id,
            })
        if not self.approval_model:
            approval_line_model = self.env['ir.model'].search([('model', '=', 'approval.line')])
            self.approval_model = self.env['ir.model.fields'].sudo().create({
                'ttype': 'many2one',
                'relation': self.model_id.model,
                'name': 'x_approval_model' + str(self.id),
                'field_description': 'Approval Model',
                'model_id': approval_line_model.id,
            })
        if not self.check_old_records_id:
            self.check_old_records_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_check_old_records',
                'field_description': 'Disable Old Record  Approval',
                'readonly': 'True',
                'store': 'True',
                'model_id': self.model_id.id,
                'depends': 'state,x_approval_id',
                'compute': """
for record in self:
    for rec in record:
        if rec.x_check_old_records:
            rec.write({'x_need_to_approve': False, 'x_multi_state': False})
        """
            })

        if not self.approver_ids or not self.env['ir.model.fields'].search(
                [('name', '=', 'x_approval_model' + str(self.id))]):
            self.approver_ids = self.env['ir.model.fields'].sudo().create({
                'ttype': 'one2many',
                'relation': 'approval.line',
                'relation_field': 'x_approval_model' + str(self.id),
                'name': 'x_approver_ids',
                'field_description': 'Approvers',
                'model_id': self.model_id.id,
                'readonly': 'True',
                'store': 'True',
                'depends': 'state,x_approval_id',
                'compute': """
lines=[(5,0,0)]
for approver in self.x_approval_id.users:
    if self.x_approval_id.enable_time_limit and not self.x_approval_id.individual_time_limit:
        val = {
            'approver_id': approver.user_ids.id,
            'sequence': approver.sequence,
            'approval_status': 'approve',
            'approval_id': self.x_approval_id.id,
            'time_limit' : approver.approver_time_limit,
            'start_date': datetime.datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S')
            }
    elif self.x_approval_id.enable_time_limit and self.x_approval_id.individual_time_limit:
        val = {
            'approver_id': approver.user_ids.id,
            'sequence': approver.sequence,
            'approval_status': 'approve',
            'approval_id': self.x_approval_id.id,
            'time_limit' : approver.individual_time_limit,
            'start_date': datetime.datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S')
            }
    else:
        val = {
            'approver_id': approver.user_ids.id,
            'sequence': approver.sequence,
            'approval_status': 'approve',
            'approval_id': self.x_approval_id.id,
            'start_date': datetime.datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S')
            }
    lines.append((0, 0, val))
    self.write({'x_approver_ids':lines})
    """
            })

            if not self.check_approvers_list:
                model_name = self.model_id.name
                self.check_approvers_list = self.env['ir.model.fields'].sudo().create({
                    'ttype': 'boolean',
                    'name': 'x_check_approvers_list',
                    'field_description': 'Add missing Approves to New records',
                    'readonly': 'True',
                    'store': False,
                    'model_id': self.model_id.id,
                    'depends': 'state',
                    'compute': """
for record in self:
    record['x_check_approvers_list'] = False
    current_moodel = record._context.get("active_model")
    approval_id = record.env['dynamic.approval'].sudo().search([('model_id', '=', '%s'""" % model_name + """)])
    if not record.x_approval_id and not record.x_check_old_records:
        record.write({'x_approval_id': approval_id, 'x_check_approvers_list': True})
    else:
        record.write({'x_check_approvers_list': False})
    """
                })

        if not self.multi_approver_status_checker_id:
            self.multi_approver_status_checker_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_approver_status_checker',
                'field_description': 'Multi Approver Status checker',
                'model_id': self.model_id.id,
                'readonly': False,
                'store': False,
                'depends': 'x_approver_ids.approval_status, state',
                'compute': """
for record in self:
  record.write({'x_approver_status_checker': False})
  if record.x_approver_ids and self.env.uid in record.x_approver_ids.mapped('approver_id').ids:
    for rec in record.x_approver_ids:
      if rec.sequence-1 == 0:
        if rec.approval_status != 'approved':
          if rec.approver_id.id == self.env.uid:
            record.write({'x_approver_status_checker': True})
            break
      else:
        for i in record.x_approver_ids.filtered(lambda l: l.approval_status != 'approved').sorted(
            lambda l: l.sequence):
            if i.approver_id.id == self.env.uid:
              record.write({'x_approver_status_checker': True})
            break
"""
            })

        if not self.group_id:
            self.group_id = group_obj.sudo().create(
                {'name': 'Approver' + ' ' + self.model_id.name,
                 'category_id': self.category_id.id,
                 'is_approve': True
                 })
            self.group_id.users = self.users.user_ids
            group_xml_id = _export_xml_id(self.group_id)
        else:
            self.group_id.users = self.users.user_ids

        if self.remove_reports:
            data = self.env[self.model_id.model].fields_view_get(view_id=None, toolbar=True, submenu=False)
            report_ids = [x.get('id') for x in data['toolbar']['print']]
            reports = self.env['ir.actions.report'].browse(report_ids)
            self.report_action_ids = reports
            reports.unlink_action()

        if not self.approve_server_action_id:
            code = ("""
for user in record.x_approver_ids.filtered(lambda l: l.approver_id == env.user):
    user.write({'approval_status' : 'approved','approval_email_status': 'sent','end_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    parallel_approvers_case = record.x_approver_ids.mapped('sequence')
    record.write({'x_check_parllel_approval': False})
    if len(parallel_approvers_case) > 1:
        if parallel_approvers_case[1] == parallel_approvers_case[0]:
            record.write({'x_check_parllel_approval': True})
        if not record.x_check_parllel_approval:
            if user.sequence == 1:
                    duration =  (user.end_date - user.start_date)
                    user.write({'approval_duration' : duration})
            else:
                    current_user_sequence = user.sequence
                    prv_approver = record.x_approver_ids.filtered(lambda l: l.sequence == current_user_sequence - 1)
                    ind_duartion = (user.end_date - prv_approver.end_date)
                    user.write({'approval_duration' : ind_duartion})
        else:
             if user.sequence == 1 :
                duration =  (user.end_date - user.start_date)
                user.write({'approval_duration' : duration})
    else:
        if user.sequence == 1 :
            duration =  (user.end_date - user.start_date)
            user.write({'approval_duration' : duration})         
    user_id = env.user
    mail_url = str(
                    record.env["ir.config_parameter"].sudo().get_param("web.base.url")) + '/web#' + 'id=' + str(
                    record.id) + '&model=' + str(record._name) + '&view_type=form'
    record.env['mail.mail'].sudo().create({
                    'subject': record._description + ' Approved',
                    'author_id': str(user_id.partner_id.id),
                    'email_from': str(user.approver_id.login),
                    'email_to': str(record.create_uid.login),
                    'body_html':
                        '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">'
                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
                        '<tbody>'
                        '<!-- HEADER -->'
                        '<tr>'
                        '<td align="center" style="min-width: 590px;">'
                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                        '<tr>'
                        '<td valign="middle">'
                        '<span style="font-size: 10px;">' 'Approval Request Approved''</span>''<br/>' +
                        '<span style="font-size: 20px; font-weight: bold;">' + record.name + '</span>'
                         '</td>'
                         '<td valign="middle" align="right">'
                         '<img src="/logo.png?company=" + record.company_id.id + style="padding: 0px; margin: 0px; height: auto; width: 80px;"/>'
                         '</td>'
                         '</tr>'
                         '<tr>''<td colspan="2" style="text-align:center;">'
                         '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                         '</td>''</tr>'
                         '</table>'
                         '</td>'
                         '</tr>'
                         '<!-- CONTENT -->'
                         '<tr>'
                         '<td align="center" style="min-width: 590px;">'
                         '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                         '<tr>'
                         '<td valign="top" style="font-size: 13px;">'
                         '<div>'
                         'Dear' + ' ' + record.create_uid.name + ',' '<br/>''<br/>'
                         'Your  approval  request ' + record.name + ' ' + 'is Approved by ' +user.approver_id.name+ '.'
                         '<br/>''<br/>'
                         '<div style="margin: 16px 0px 16px 0px;">'                                               
                         '<span>'
                         '<a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href=' + mail_url + '>View Record</a>'
                         '</span>'
                        '</div>'
                        '<br/>''<br/>' 
                        'Best regards''<br/>'
                        '</div>'
                        '</td>'
                        '</tr>'
                        '<tr>'
                        '<td style="text-align:center;">'
                        '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                        '</td>'
                        '</tr>'
                        '</table>'
                        '</td>'
                        '</tr>'
                        '<!-- FOOTER -->'
                        '<tr>'
                        '<td align="center" style="min-width: 590px;">'
                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                        '<tr>'
                        '<td valign="middle" align="left">'
                        + user_id.company_id.name +
                        '<br/>'
                        + user_id.company_id.phone +
                        '</td>'
                        '<td valign="middle" align="right">'
                        '<t t-if="%s" % +user_id.company_id.email>'
                        '<a href="mailto:%s % +user_id.company_id.email+" style="text-decoration:none; color: #5e6061;">'
                        +user_id.company_id.email+
                        '</a>'
                        '</t>' 
                        '<br/>'
                        '<t t-if="%s % +user_id.company_id.website+ ">'
                        '<a href="%s % +user_id.company_id.website+" style="text-decoration:none; color: #5e6061;">'
                        +user_id.company_id.website+
                        '</a>'
                        '</t>'
                        '</td>'
                        '</tr>'
                        '</table>'
                        '</td>'
                        '</tr>'
                        '</tbody>'
                        '</table>'
                }).send()
    current_user = record.x_approver_ids.filtered(lambda l: l.approver_id == env.user)
    sequ = current_user.sequence + 1
    next_user_id = record.x_approver_ids.filtered(lambda l: l.sequence == sequ)
    if next_user_id:
        record.env['mail.mail'].sudo().create({
                        'subject': record._description + ' Approval',
                        'author_id': str(user_id.partner_id.id),
                        'email_from': str(record.create_uid.login),
                        'email_to': str(next_user_id.approver_id.login),
                        'body_html':
                            '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
                            '<tbody>'
                            '<!-- HEADER -->'
                            '<tr>'
                            '<td align="center" style="min-width: 590px;">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                            '<tr>'
                            '<td valign="middle">'
                            '<span style="font-size: 10px;">' 'Need Approval''</span>''<br/>' +
                            '<span style="font-size: 20px; font-weight: bold;">' + record.name + '</span>'
                             '</td>'
                             '<td valign="middle" align="right">'
                             '<img src="/logo.png?company=" + record.company_id.id + style="padding: 0px; margin: 0px; height: auto; width: 80px;"/>'
                             '</td>'
                             '</tr>'
                             '<tr>''<td colspan="2" style="text-align:center;">'
                             '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                             '</td>''</tr>'
                             '</table>'
                             '</td>'
                             '</tr>'
                             '<!-- CONTENT -->'
                             '<tr>'
                             '<td align="center" style="min-width: 590px;">'
                             '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                             '<tr>'
                             '<td valign="top" style="font-size: 13px;">'
                             '<div>'
                             'Dear' + ' ' + str(next_user_id.approver_id.name) + ',' '<br/>''<br/>'
                             'You have a new approval request from ' + record.create_uid.name + ' ' + 'of ' +record.name+ '.' '<br/>'
                             '<span style="color: red;">' 'The approval time limit of the request is ' + str(user.time_limit) + ' Hour .' '</span>'
                             '<br/>''<br/>'
                             '<div style="margin: 16px 0px 16px 0px;">'                                               
                             '<span>'
                             '<a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href=' + mail_url + '>View Record</a>'
                             '</span>'
                            '</div>'
                            '<br/>''<br/>' 
                            'Best regards''<br/>'
                            '</div>'
                            '</td>'
                            '</tr>'
                            '<tr>'
                            '<td style="text-align:center;">'
                            '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                            '</td>'
                            '</tr>'
                            '</table>'
                            '</td>'
                            '</tr>'
                            '<!-- FOOTER -->'
                            '<tr>'
                            '<td align="center" style="min-width: 590px;">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                            '<tr>'
                            '<td valign="middle" align="left">'
                            + str(next_user_id.approver_id.company_id.name) +
                            '<br/>'
                            + str(next_user_id.approver_id.company_id.phone) +
                            '</td>'
                            '<td valign="middle" align="right">'
                            '<t t-if="%s" % + str(next_user_id.approver_id.company_id.email) +>'
                            '<a href="mailto:%s % + str(next_user_id.approver_id.company_id.email) +" style="text-decoration:none; color: #5e6061;">'
                            + str(next_user_id.approver_id.company_id.email) +
                            '</a>'
                            '</t>' 
                            '<br/>'
                            '<t t-if="%s % + str(next_user_id.approver_id.company_id.website) + ">'
                            '<a href="%s % + str(next_user_id.approver_id.company_id.website) +" style="text-decoration:none; color: #5e6061;">'
                            + str(next_user_id.approver_id.company_id.website) +
                            '</a>'
                            '</t>'
                            '</td>'
                            '</tr>'
                            '</table>'
                            '</td>'
                            '</tr>'
                            '</tbody>'
                            '</table>'
                    }).send()
    if current_user.sequence == next_user_id.sequence - 1:
        next_user_id.write({'approval_email_status': 'sent', 'start_date': datetime.datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S') })
    else:
        next_user_id.write({'approval_email_status': 'sent'})
    current_moodel = record._context.get("active_model")
    if 'approve' not in record.x_approver_ids.mapped('approval_status'):
        record.write({'x_approve':True, 'x_approve_state':'approved', 'x_need_to_approve': False,'x_multi_state': False}) 
    if record.env['ir.model'].search([('model', '=', current_moodel)]).is_mail_thread:
        record.message_post(body=record._description+" is Approved, and the Approval Duration is " + str(user.approval_duration)+" .", subject="Approved")
        record.message_post(body="The approval request is Approved and Info mail sent to the created user " + record.create_uid.name+" .", subject="Approved Mail")
        parallel_approvers_case = record.x_approver_ids.mapped('sequence')
        if next_user_id:
            if len(parallel_approvers_case) > 1 and parallel_approvers_case[1] != parallel_approvers_case[0]:
                record.message_post(body="The " + record._description + " Approval request email is sent to the next approver " + next_user_id.approver_id.name+" .", subject="Email Sent")
""")
            # """env['ir.actions.report'].browse("%s").create_action()""" % self.report_action_ids.id)
            self.approve_server_action_id = self.env['ir.actions.server'].sudo().create({'name': approve_action_name,
                                                                                         'model_id': self.model_id.id,
                                                                                         'state': 'code',
                                                                                         'code': code})

        code = ("""
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'reject.reason',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Approval Reject Reason',
            'context': {'origin':record},
        }""")

        if not self.reject_server_action_id:
            self.reject_server_action_id = self.env['ir.actions.server'].sudo().create({'name': reject_action_name,
                                                                                        'model_id': self.model_id.id,
                                                                                        'state': 'code',
                                                                                        'code': code})
        if not self.re_send_server_action_id:
            code = ("""
current_moodel = record._context.get("active_model")
for user in record.x_approver_ids.filtered(lambda l: l.approval_status != 'approve'):
    user.write({'approval_status' : 'approve', 'approval_email_status': 'draft'})
    if 'approve' in record.x_approver_ids.mapped('approval_status'):
        record.write({'x_approve':True, 'x_approve_state':'approve'})
    if record.env['ir.model'].search([('model', '=', current_moodel)]).is_mail_thread:   
        record.message_post(body=record._description+" Approval request is resubmitted .", subject="Resubmitted")
    """)
            self.re_send_server_action_id = self.env['ir.actions.server'].sudo().create(
                {'name': re_send_action_name,
                 'model_id': self.model_id.id,
                 'state': 'code',
                 'code': code})

        if not self.email_status_checker_id:
            self.email_status_checker_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_email_status_checker',
                'field_description': 'Approval Email Status checker',
                'model_id': self.model_id.id,
                'readonly': False,
                'store': False,
                'depends': 'x_approver_ids.approval_status, state',
                'compute': """
user_id = self.env.user
subject = self._description + ' Approval'
current_moodel = self._context.get("active_model")
for record in self:
    record.write({'x_email_status_checker': False})
    if record.x_approver_ids and record.id:
        for rec in record.x_approver_ids:
          if rec.sequence == 1:
            if rec.approval_email_status != 'sent' and rec.approval_status != 'approved':
                rec.write({'approval_email_status': 'sent'})
                record.write({'x_email_status_checker': True})
                if record.x_email_status_checker:
                     mail_url=str(self.env["ir.config_parameter"].sudo().get_param("web.base.url"))+'/web#'+'id='+str(record.id)+'&model='+str(record._name)+'&view_type=form'
                     self.env['mail.mail'].sudo().create({
                        'subject': subject,
                        'author_id': str(user_id.partner_id.id),
                        'email_from': str(record.create_uid.login),
                        'email_to': str(rec.approver_id.login),
                        'body_html': 
                        '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">'
                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
                        '<tbody>'
                            '<!-- HEADER -->'
                            '<tr>'
                                '<td align="center" style="min-width: 590px;">'
                                    '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                                        '<tr>'
                                            '<td valign="middle">'
                                                '<span style="font-size: 10px;">' 'Need Approval''</span>''<br/>' +
                                                '<span style="font-size: 20px; font-weight: bold;">' + record.name + '</span>'
                                            '</td>'
                                            '<td valign="middle" align="right">'
                                                '<img src="/logo.png?company=" + record.company_id.id + style="padding: 0px; margin: 0px; height: auto; width: 80px;"/>'
                                            '</td>'
                                        '</tr>'
                                        '<tr>''<td colspan="2" style="text-align:center;">'
                                            '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                                        '</td>''</tr>'
                                    '</table>'
                                '</td>'
                            '</tr>'
                            '<!-- CONTENT -->'
                             '<tr>'
                                '<td align="center" style="min-width: 590px;">'
                                    '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                                        '<tr>'
                                            '<td valign="top" style="font-size: 13px;">'
                                            '<div>'
                                                'Dear' + ' ' +rec.approver_id.name+ ',' '<br/>''<br/>'
                                                'You have a new Approval  request from' + ' ' +record.create_uid.name + ' ' + 'of' + ' ' + record.name + '.' '<br/>'
                                                '<span style="color: red;">' 'The approval time limit of the request is ' + str(rec.time_limit) + ' Hour .' '</span>'
                                                '<br/>''<br/>'
                                                '<div style="margin: 16px 0px 16px 0px;">'
                                                    '<span>'
                                                        '<a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href='+mail_url+'>View Record</a>'
                                                    '</span>'
                                                '</div>'
                                                '<br/>''<br/>' +
                                                'Best regards' + '<br/>'
                                            '</div>'
                                            '</td>'
                                        '</tr>'
                                        '<tr>'
                                            '<td style="text-align:center;">'
                                                '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                                            '</td>'
                                        '</tr>'
                                    '</table>'
                                '</td>'
                            '</tr>' 
                            '<!-- FOOTER -->'
                            '<tr>'
                            '<td align="center" style="min-width: 590px;">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                            '<tr>'
                            '<td valign="middle" align="left">'
                            +user_id.company_id.name+
                            '<br/>'
                            +user_id.company_id.phone+
                            '</td>'
                            '<td valign="middle" align="right">'
                            '<t t-if="%s" % +user_id.company_id.email>'
                            '<a href="mailto:%s % +user_id.company_id.email+" style="text-decoration:none; color: #535556;">'
                            +user_id.company_id.email+ 
                            '</a>'
                            '</t>' 
                            '<br/>'
                            '<t t-if="%s % +user_id.company_id.website+ ">'
                            '<a href="%s % +user_id.company_id.website+" style="text-decoration:none; color: #535556;">'
                            +user_id.company_id.website+
                            '</a>'
                            '</t>'
                            '</td>'
                            '</tr>'
                            '</table>'
                            '</td>'
                            '</tr>'
                        '</tbody>'
                        '</table>'
                     }).send()
                if record.env['ir.model'].search([('model', '=', self._name)]).is_mail_thread:
                    if record.company_id.id in record.x_approver_ids.approval_id.company_id.ids:
                        record.message_post(body=record._description+" approval request mail is sent to the first approver " +rec.approver_id.name+ " .", subject="First Approval Mail Shared")"""
            })

        if not self.fully_approved_field_id:
            self.fully_approved_field_id = self.env['ir.model.fields'].sudo().create({
                'ttype': 'boolean',
                'name': 'x_fully_approved',
                'field_description': 'Fully Approved',
                'model_id': self.model_id.id,
                'readonly': False,
                'store': False,
                'depends': 'x_approver_ids.approval_status, state',
                'compute': """             
for record in self:
 if not record.x_approver_ids.filtered(lambda l: l.approval_status != 'approved'):
  record.write({'x_fully_approved' : True})
                 """
            })

        if not self.check_approval_delay:
            if self.enable_time_limit:
                sheduled_action_name = self.model_id.name + "Approval Delay checker"
                model = self.model_id.model
                model_name = self.model_id.name
                self.check_approval_delay = self.env['ir.cron'].sudo(). \
                    create({'name': sheduled_action_name,
                            'active': True,
                            'model_id': self.model_id.id,
                            'interval_number': self.delay_time,
                            'interval_type': self.delay_type,
                            'nextcall': datetime.now(),
                            'numbercall': -1,
                            'priority': 5,
                            'doall': True,
                            'code': """
for x_approval_id in env['dynamic.approval'].sudo().search([('model_id', '=', '%s'""" % model_name +""")]):
  if x_approval_id.is_reminder:
    data = env['%s'""" % model +"""].search([('x_approve_state', '=', 'approve'),('x_check_old_records', '=', False),('x_reminder_mail', '=', False)])
  else:
    data = env['%s'""" % model +"""].search([('x_approve_state', '=', 'approve'),('x_check_old_records', '=', False)])
for record in data:
     for delayed_approver in record.x_approver_ids:
            hour = delayed_approver.start_date.hour
            dealy_date = delayed_approver.start_date.replace(
                hour=delayed_approver.time_limit + hour)
            if dealy_date <= datetime.datetime.now() and delayed_approver.approval_status == 'approve':
                delayed_approver.write({'delay': True, 'authority_email_status': 'sent'})
                break
     mail_url = str(
     env["ir.config_parameter"].sudo().get_param("web.base.url")) + '/web#' + 'id=' + str(
     record.id) + '&model=' + str(record._name) + '&view_type=form'
     if record.x_approval_id.enable_time_limit:
        for approver in record.x_approver_ids.filtered(lambda l: l.time_limit and l.approval_status == 'approve' and l.delay):
            if not approver.is_send:
                env['mail.mail'].sudo().create({
                    'subject': record._description + ' Approval Delayed',
                    'author_id': str(approver.approver_id.partner_id.id),
                    'email_from': str(approver.approver_id.login),
                    'email_to': str(record.create_uid.login),
                    'body_html': '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
                            '<tbody>'
                            '<!-- HEADER -->'
                            '<tr>'
                            '<td align="center" style="min-width: 590px;">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                            '<tr>'
                            '<td valign="middle">'
                            '<span style="font-size: 10px;">' 'Approval Delayed''</span>''<br/>' +
                            '<span style="font-size: 20px; font-weight: bold;">' + record.name + '</span>'
                             '</td>'
                             '<td valign="middle" align="right">'
                             '<img src="/logo.png?company=" + record.company_id.id + style="padding: 0px; margin: 0px; height: auto; width: 80px;"/>'
                             '</td>'
                             '</tr>'
                             '<tr>''<td colspan="2" style="text-align:center;">'
                             '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                             '</td>''</tr>'
                             '</table>'
                             '</td>'
                             '</tr>'
                             '<!-- CONTENT -->'
                             '<tr>'
                             '<td align="center" style="min-width: 590px;">'
                             '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                             '<tr>'
                             '<td valign="top" style="font-size: 13px;">'
                             '<div>'
                             'Dear' + ' ' + record.create_uid.name + ',' '<br/>''<br/>'
                             'Your  approval  request ' + record.name + ' ' + 'is Delayed by ' +approver.approver_id.name+ '.'
                             'Its escalated to the authority ' + str(record.x_approval_id.user_ids.mapped('partner_id.name')) + ' .'
                             '<br/>''<br/>'
                             '<div style="margin: 16px 0px 16px 0px;">'
                             '<span>'
                             '<a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href=' + mail_url + '>View Record</a>'
                             '</span>'
                            '</div>'
                            '<br/>''<br/>'
                            'Best regards''<br/>'
                            '</div>'
                            '</td>'
                            '</tr>'
                            '<tr>'
                            '<td style="text-align:center;">'
                            '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                            '</td>'
                            '</tr>'
                            '</table>'
                            '</td>'
                            '</tr>'
                            '<!-- FOOTER -->'
                            '<tr>'
                            '<td align="center" style="min-width: 590px;">'
                            '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                            '<tr>'
                            '<td valign="middle" align="left">'
                            + approver.approver_id.company_id.name +
                            '<br/>'
                            + approver.approver_id.company_id.phone +
                            '</td>'
                            '<td valign="middle" align="right">'
                            '<t t-if="%s" % + approver.approver_id.company_id.email +>'
                            '<a href="mailto:%s % +approver.company_id.email+" style="text-decoration:none; color: #454748;">'
                            + approver.approver_id.company_id.email +
                            '</a>'
                            '</t>'
                            '<br/>'
                            '<t t-if="%s" % + approver.approver_id.company_id.website +>'
                            '<a href="%s % +approver.company_id.website+" style="text-decoration:none; color: #454748;">'
                            + approver.approver_id.company_id.website +
                            '</a>'
                            '</t>'
                            '</td>'
                            '</tr>'
                            '</table>'
                            '</td>'
                            '</tr>'
                            '</tbody>'
                            '</table>'
                    }).send()
                approver.write({'is_send': True})
            for authority in record.x_approval_id.user_ids:
                env['mail.mail'].sudo().create({
                                'subject': record._description + ' Approval Delayed',
                                'author_id': str(approver.approver_id.partner_id.id),
                                'email_from': str(approver.approver_id.login),
                                'email_to':  str(authority.login),
                                'body_html': '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">'
                                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
                                        '<tbody>'
                                        '<!-- HEADER -->'
                                        '<tr>'
                                        '<td align="center" style="min-width: 590px;">'
                                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                                        '<tr>'
                                        '<td valign="middle">'
                                        '<span style="font-size: 10px;">' 'Approval Delayed''</span>''<br/>' +
                                        '<span style="font-size: 20px; font-weight: bold;">' + record.name + '</span>'
                                         '</td>'
                                         '<td valign="middle" align="right">'
                                         '<img src="/logo.png?company=" + record.company_id.id + style="padding: 0px; margin: 0px; height: auto; width: 80px;"/>'
                                         '</td>'
                                         '</tr>'
                                         '<tr>''<td colspan="2" style="text-align:center;">'
                                         '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                                         '</td>''</tr>'
                                         '</table>'
                                         '</td>'
                                         '</tr>'
                                         '<!-- CONTENT -->'
                                         '<tr>'
                                         '<td align="center" style="min-width: 590px;">'
                                         '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                                         '<tr>'
                                         '<td valign="top" style="font-size: 13px;">'
                                         '<div>'
                                         'Dear' + ' ' + authority.name + ',' '<br/>''<br/>'
                                         'The  approval  request ' + record.name + ' ' + 'is Dealyed by ' +approver.approver_id.name+ '.'
                                         '<br/>''<br/>'
                                         '<div style="margin: 16px 0px 16px 0px;">'
                                         '<span>'
                                         '<a style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href=' + mail_url + '>View Record</a>'
                                         '</span>'
                                        '</div>'
                                        '<br/>''<br/>'
                                        'Best regards''<br/>'
                                        '</div>'
                                        '</td>'
                                        '</tr>'
                                        '<tr>'
                                        '<td style="text-align:center;">'
                                        '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
                                        '</td>'
                                        '</tr>'
                                        '</table>'
                                        '</td>'
                                        '</tr>'
                                        '<!-- FOOTER -->'
                                        '<tr>'
                                        '<td align="center" style="min-width: 590px;">'
                                        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">'
                                        '<tr>'
                                        '<td valign="middle" align="left">'
                                        + approver.approver_id.company_id.name +
                                        '<br/>'
                                        + approver.approver_id.company_id.phone +
                                        '</td>'
                                        '<td valign="middle" align="right">'
                                        '<t t-if="%s" + approver.approver_id.company_id.email +>'
                                        '<a href="mailto:%s % +approver.company_id.email+" style="text-decoration:none; color: #454748;">'
                                        + approver.approver_id.company_id.email +
                                        '</a>'
                                        '</t>'
                                        '<br/>'
                                        '<t t-if="%s" % + approver.approver_id.company_id.website +>'
                                        '<a href="%s % +approver.company_id.website+" style="text-decoration:none; color: #454748;">'
                                        + approver.approver_id.company_id.website +
                                        '</a>'
                                        '</t>'
                                        '</td>'
                                        '</tr>'
                                        '</table>'
                                        '</td>'
                                        '</tr>'
                                        '</tbody>'
                                        '</table>'
                                }).send()
        record.write({'x_reminder_mail': True})
        if record.env['ir.model'].search([('model', '=', '""" + model + """')]).is_mail_thread:
            record.message_post(body="Approval request " + record.name + " delayed by " + approver.approver_id.name + "." "Its escalated to the authority" + str(record.x_approval_id.user_ids.mapped('partner_id.name')) + " ." , subject="Approval Request Delayed")
            record.message_post(body="The approval request is delayed and Info mail sent to the created user " + record.create_uid.name+" .", subject="Approval Delayed")
                                """

                            })
        state_data = self.model_states.mapped('value')
        if not self.tree_view_id:
            if self.add_approval_status_to_tree:
                inherit_tree_view_name = self.tree_view_name.name + "_dynamic_approval"
                tree_view_arch_base = _(
                    '''<?xml version="1.0"?>'''
                    '''<data>'''
                    '''<xpath expr="//field[@name='state']" position="after">'''
                    '''<field name="x_approve_state" groups="base.group_multi_company" attrs='{"invisible": [("company_id", "not in", %s)]}'
                    widget="badge" decoration-success="x_approve_state == 'approved'" 
                    decoration-info="x_approve_state == 'approve'" decoration-danger="x_approve_state == 'reject'"/>'''
                    '''</xpath>'''
                    '''</data>''') % str(self.company_id.ids)
                self.tree_view_id = self.env['ir.ui.view'].sudo().create(
                    {'name': inherit_tree_view_name,
                     'type': 'tree',
                     'model': self.model_id.model,
                     'mode': 'extension',
                     'inherit_id': self.tree_view_name.id,
                     'arch_base': tree_view_arch_base,
                     'active': True})

        if not self.search_view_id:
            if self.add_approval_status_to_tree:
                inherit_search_view_name = self.search_view_name.name + "_dynamic_approval"
                search_view_arch_base = _(
                    '''<?xml version="1.0"?>'''
                    '''<data>'''
                    '''<xpath expr="//search/group" position="inside">'''
                    '''<filter string="Approved" name="Approved" domain="[('x_approve_state', '=', 'approved')]"/>'''
                    '''<filter string="Waiting For Approval" 
                    name="Waiting For Approval" domain="[('x_approve_state', '=', 'approve'),
                    ('x_check_old_records', '!=', 'True')]"/>'''
                    '''<filter string="Rejected" name="Rejected" domain="[('x_approve_state', '=', 'reject')]"/>'''
                    '''<filter string="Approver" name="groupby_date" domain="[]" context="{'group_by': 'x_approver_ids'}"/>'''
                    '''</xpath>'''
                    '''</data>''')
                self.search_view_id = self.env['ir.ui.view'].sudo().create(
                    {'name': inherit_search_view_name,
                     'type': 'search',
                     'model': self.model_id.model,
                     'mode': 'extension',
                     'inherit_id': self.search_view_name.id,
                     'arch_base': search_view_arch_base,
                     'active': True})

        if not self.view_id:
            arch_base = _('''<?xml version="1.0"?>'''
                          '''<data>'''
                          '''<xpath expr="//header" position="after">'''
                          '''<header>'''
                          '''<button name="%s" string="Approve" 
                           class="oe_highlight" type="action" '''
                          '''attrs='{"invisible": ["|",("x_approve_state", "in", ["reject","approved"]),'''
                          '''("x_approver_status_checker", "=", False)]}' 
                          groups="%s"/> '''
                          '''<button name="%s" string="Reject" class="oe_highlight" 
                          type="action" '''
                          '''attrs='{"invisible": ["|",("x_approve_state", "in", ["reject", "approved"]),'''
                          '''("x_approver_status_checker", "=", False)]}' groups="%s"/>'''
                          '''<button name="%s" string="Re-Send" 
                          class="oe_highlight" type="action" '''
                          '''attrs='{"invisible": [("x_approve_state", "in", ["approve", "approved"])]}'/>'''
                          '''<field name="x_approve_state" widget="statusbar" '''
                          '''statusbar_visible="approved,approve,reject"/>'''
                          '''</header>'''
                          '''</xpath>'''
                          '''<xpath expr="//sheet" position="inside">'''
                          '''<field name="x_need_to_approve" invisible="1"/>'''
                          '''<field name="x_multi_state" invisible="1"/>'''
                          '''<field name="x_reminder_mail" invisible="1"/>'''
                          '''<field name="x_check_parllel_approval"  
                          invisible="1"/>'''
                          '''<field name="x_approver_status_checker" 
                          invisible="1"/>'''
                          '''<field name="x_email_status_checker" 
                          invisible="1"/>'''
                          '''<field name="x_check_old_records" 
                          invisible="1"/>'''
                          '''<field name="x_check_approvers_list" 
                          invisible="1"/>'''
                          '''<notebook attrs='{"invisible": [("company_id", "not in", %s)]}'>'''
                          '''<page string="Approves" name="approves">'''
                          '''<field name="x_approval_id" invisible="1" force_save="1"/>'''
                          '''<field name="x_approver_ids" mode="tree">'''
                          '''<tree>'''
                          '''<field name="sequence"/>'''
                          '''<field name="approval_id"/>'''
                          '''<field name="approver_id"/>'''
                          '''<field name="approval_status"/>'''
                          '''<field name="approval_email_status"/>'''
                          '''<field name="reject_reason"/>'''
                          '''<field name="time_limit" widget="float_time"/>'''
                          '''<field name="delay"/>'''
                          '''<field name="authority_email_status"/>'''
                          '''<field name="is_send" invisible="1"/>'''
                          '''<field name="approval_duration"/>'''
                          '''<field name="start_date" invisible="1"/>'''
                          '''<field name="end_date" invisible="1"/>'''
                          '''</tree>'''
                          '''</field>'''
                          '''</page>'''
                          '''</notebook>'''
                          '''</xpath>'''
                          '''<xpath expr="//form/header[1]" position="attributes">'''
                          '''<attribute name="attrs">{"invisible" : ["&amp;","&amp;",("state", "in", %s),'''
                          '''("x_need_to_approve", "=", True), ("company_id", "in", %s)]}</attribute>'''
                          '''</xpath>'''
                          '''<xpath expr="//form/header[2]" position="attributes">'''
                          '''<attribute name="attrs">{"invisible" : ["|","|",("state","not in", %s),'''
                          '''("x_multi_state","!=", True), ("company_id", "not in", %s)]}</attribute>'''
                          '''</xpath>'''
                          '''</data>''') % (
                            str(self.approve_server_action_id.id),
                            group_xml_id, str(self.reject_server_action_id.id),
                            group_xml_id, str(self.re_send_server_action_id.id), self.company_id.ids,
                            state_data, self.company_id.ids, state_data, self.company_id.ids)
            self.view_id = self.env['ir.ui.view'].sudo().create({'name': inherit_name,
                                                                 'type': 'form',
                                                                 'model': self.model_id.model,
                                                                 'mode': 'extension',
                                                                 'inherit_id': inherit_id.id,
                                                                 'arch_base': arch_base,
                                                                 'active': True})
            cr = self.env.cr
            table_name = self.model_id.model.replace('.', '_')
            sql = """update  %s set x_check_old_records = %s """ % (str(table_name), True)
            cr.execute(sql)

            for record in self.action_id:
                for rec in record:
                    if rec.context:
                        action_context = eval(rec.context)
                        action_context['default_x_need_to_approve'] = True
                        action_context['default_x_multi_state'] = True
                        action_context['default_x_approve_state'] = 'approve'
                        action_context['default_' + self.approval_id.name] = self.id
                        rec.write({'context': str(action_context)})
                    else:
                        raise UserError(_("You choiced model we can't create Approval."
                                          "Because the model not have the Context."))

    def allow_multi_state_approval(self):
        self.write({'state': 'multi_state_activated'})
        self.message_post(body="Multi State Approval Activated",
                          subject="Multi State Approval")
        automation_action_name = self.model_id.name + ' Automate Action'
        status = self.model_id.field_id.filtered(lambda l: l.name == 'state')
        if not self.automation_action_id:
            automation_server_action_id = self.env['ir.server.object.lines']. \
                sudo().create([
                {'col1': self.need_to_approve_id.id,
                 'evaluation_type': 'value',
                 'value': 'True'},
                {'col1': self.multi_state_field_id.id,
                 'evaluation_type': 'value',
                 'value': 'True'},
                {'col1': self.approve_state_id.id,
                 'evaluation_type': 'value',
                 'value': 'approve'}])
            self.automation_action_id = self.env['base.automation'].sudo(). \
                create({'name': automation_action_name,
                        'model_id': self.model_id.id,
                        'active': True,
                        'trigger': 'on_write',
                        'trigger_field_ids': status,
                        'state': 'object_write',
                        'fields_lines': automation_server_action_id.ids
                        })

    def apply_old_record(self):
        approval_id = self.env['dynamic.approval'].search([('model_id', '=', self.model_id.model)]).id
        cr = self.env.cr
        table_name = self.model_id.model.replace('.', '_')
        sql = """update  %s set x_need_to_approve = %s, x_multi_state = %s, x_approval_id = %s, x_approve_state = '%s'
        WHERE x_check_old_records = %s """ % (str(table_name), True, True, str(approval_id), str('approve'), True)
        cr.execute(sql)
        self.write({'state': 'old'})
        self.message_post(body="Approval applied to Old records",
                          subject="Applied to Old Records")

    def update_approvers_list(self):
        self.write({'state': 'update'})
        self.message_post(body="Need To Change Approvers List",
                          subject="Approvers List")

    def apply_changes(self):
        self.write({'state': 'apply'})
        self.message_post(body="The Approves List Updated",
                          subject="Approvers List")

    def unlink(self):
        reports_data = self.env['ir.actions.report'].search([('model', '=', self.model_id.model)])
        reports_data.create_action()
        self.view_id.sudo().unlink()
        self.tree_view_id.sudo().unlink()
        self.search_view_id.sudo().unlink()
        self.automation_action_id.fields_lines.sudo().unlink()
        self.automation_action_id.sudo().unlink()
        self.approve_server_action_id.sudo().unlink()
        self.reject_server_action_id.sudo().unlink()
        self.re_send_server_action_id.sudo().unlink()
        self.custom_field_id.sudo().unlink()
        self.approve_state_id.sudo().unlink()
        self.reject_reason_id.sudo().unlink()
        self.need_to_approve_id.sudo().unlink()
        self.parallel_approval_duration_id.sudo().unlink()
        self.multi_state_field_id.sudo().unlink()
        self.email_template_id.sudo().unlink()
        self.email_template_server_action_id.sudo().unlink()
        self.approve_server_action_id.sudo().unlink()
        self.fully_approved_field_id.depends = False
        self.fully_approved_field_id.sudo().unlink()
        self.multi_approver_status_checker_id.depends = False
        self.multi_approver_status_checker_id.sudo().unlink()
        self.email_status_checker_id.depends = False
        self.email_status_checker_id.sudo().unlink()
        self.check_old_records_id.sudo().unlink()
        self.reminder_mail.sudo().unlink()
        self.approver_ids.depends = False
        self.group_id.sudo().unlink()
        self.approval_id.sudo().unlink()
        self.approver_ids.sudo().unlink()
        self.check_approvers_list.depends = False
        self.check_approvers_list.sudo().unlink()
        self.approval_model.sudo().unlink()
        if self.check_approval_delay:
            self.check_approval_delay.sudo().unlink()
        return super(Approval, self).unlink()

    def action_approval_cancel(self):
        reports_data = self.env['ir.actions.report'].search([('model', '=', self.model_id.model)])
        reports_data.create_action()
        self.view_id.sudo().unlink()
        self.tree_view_id.sudo().unlink()
        self.search_view_id.sudo().unlink()
        self.automation_action_id.fields_lines.sudo().unlink()
        self.automation_action_id.sudo().unlink()
        self.approve_server_action_id.sudo().unlink()
        self.reject_server_action_id.sudo().unlink()
        self.re_send_server_action_id.sudo().unlink()
        self.custom_field_id.sudo().unlink()
        self.approve_state_id.sudo().unlink()
        self.reject_reason_id.sudo().unlink()
        self.need_to_approve_id.sudo().unlink()
        self.parallel_approval_duration_id.sudo().unlink()
        self.multi_state_field_id.sudo().unlink()
        self.email_template_id.sudo().unlink()
        self.email_template_server_action_id.sudo().unlink()
        self.approve_server_action_id.sudo().unlink()
        self.fully_approved_field_id.depends = False
        self.fully_approved_field_id.sudo().unlink()
        self.multi_approver_status_checker_id.depends = False
        self.multi_approver_status_checker_id.sudo().unlink()
        self.email_status_checker_id.depends = False
        self.email_status_checker_id.sudo().unlink()
        self.check_old_records_id.sudo().unlink()
        self.reminder_mail.sudo().unlink()
        self.approver_ids.depends = False
        self.group_id.sudo().unlink()
        self.approval_id.sudo().unlink()
        self.approver_ids.sudo().unlink()
        self.check_approvers_list.depends = False
        self.check_approvers_list.sudo().unlink()
        self.approval_model.sudo().unlink()
        if self.check_approval_delay:
            self.check_approval_delay.sudo().unlink()
        return self.write({'state': 'cancel'})
