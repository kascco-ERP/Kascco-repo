
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_man_power_order = fields.Boolean(string="Is Man Power Order", required=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    sale_orders_id = fields.Many2one('sale.order', string="Sale Order", readonly=True)




class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    project = fields.Boolean(string="Is Project",readonly=True)

