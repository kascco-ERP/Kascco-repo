# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderKeffah(models.Model):
    _inherit = 'sale.order'

    is_man_power = fields.Boolean(related="company_id.is_man_power", readonly=True)
    is_man_power_order = fields.Boolean(string="Is Man Power Order")
    sa_vat = fields.Char(related="partner_id.vat", readonly=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    product_categ_ids = fields.Many2many('product.category',string='Product Category')
    is_check = fields.Boolean(string='Is Check', related="company_id.is_man_power", readonly=True)
    hide_unit_price = fields.Boolean(string="Hide Unit Price", help="Hide unit price in the printed PDF.")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True,
                                     readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True,
                                 compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
                                   compute='_amount_all',
                                   track_visibility='always')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.onchange('partner_id')
    def get_partner(self):
        if self.partner_id:
            self.is_man_power_order = False
    
   
    def _prepare_invoice(self):
        record = super(SaleOrderKeffah, self)._prepare_invoice()
        if self.is_man_power_order == False:
            return record
        else:
            record['sale_orders_id'] = self.id
            record['is_man_power_order'] = True
            return record

    @api.depends('order_line.price_subtotal', 'order_line.price_tax',
                 'order_line.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        check = super(SaleOrderKeffah, self)._compute_amounts()
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type)
            order.amount_untaxed = sum(order_lines.mapped('price_subtotal'))
            order.amount_tax = sum(order_lines.mapped('price_tax'))
            order.tax_totals = order.amount_total
        return check

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total',
                 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )


class WorkDay(models.Model):
    _name = 'work.day'
    _description = 'work day'

    day = fields.Integer(string='Day')
    labels = fields.Many2one('day.label', string='Name Day')

    @api.depends('day','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.day
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res

class labelDay(models.Model):
    _name = 'day.label'
    _description = 'day label'

    name = fields.Char(string='Name')

class WorkHours(models.Model):
    _name = 'work.hours'
    _description = 'work hours'


    hours = fields.Integer(string='Hour')
    labels = fields.Many2one('label.label', string='Name Hour')

    @api.depends('hours','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.hours
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res

class label(models.Model):
    _name = 'label.label'
    _description = 'label'

    name = fields.Char(string='Name')


class WorkMonthly(models.Model):
    _name = 'work.monthly'
    _description = 'work monthly'


    monthly = fields.Integer(string='Month')
    labels = fields.Many2one('month.month', string='Name Month')

    @api.depends('monthly','labels')
    def name_get(self):
        res = []
        for record in self:
            name = record.monthly
            if record.labels:
                data =  str(name) + ' ' + record.labels.name
            res.append((record.id, data))
        return res


class Month(models.Model):
    _name = 'month.month'
    _description = 'Month'

    name = fields.Char(string='Name')

class SaleOrderLineKeffah(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    working_days = fields.Many2one('work.day',string="Working Days")
    working_hours = fields.Many2one('work.hours',string="Working Hours")
    monthly_hours = fields.Float(string="Monthly Hours", compute="_compute_monthly_hours_rate", store=True)
    month_rate = fields.Float(string="Monthly Rate", compute="_compute_monthly_hours_rate", store=True)
    total_monthly = fields.Float(string="Total Monthly", compute="_compute_monthly_hours_rate", store=True)
    working_month = fields.Many2one('work.monthly',string="Monthly Working Period")
    total_add_monthly = fields.Float(string="Total Monthly Period")
    is_man_power_order = fields.Boolean(string="Is Man Power Order?",compute="_onchange_is_man_power_order",store=True)


    @api.depends('order_id.is_man_power_order')
    def _onchange_is_man_power_order(self):
        for rec in self:
            if rec.order_id.is_man_power_order == True:
                rec.is_man_power_order = True
            else:
                return False

    @api.onchange('product_template_id')
    def onchange_product_cat(self):
        if self.order_id.is_man_power_order == True:
            record =  self.order_id.product_categ_ids.ids
            category_obj = self.env['product.category'].search([('id','in',[rec for rec in record])])
            products = self.env['product.template'].search([('categ_id.id','in',[rec.id for rec in category_obj])])
            return{'domain': {'product_template_id':[('id','in',products.ids)]}}
        else:
            return False

    """@api.onchange() should be set and create anatical account for customer"""

    @api.onchange('analytic_distribution')
    def get_analytic_line(self):
        plan = self.env['account.analytic.plan'].search([('project','=',True)])
        if self.order_id.is_man_power_order == True:
            analytic = self.env['account.analytic.account'].search([('partner_id','=',self.order_id.partner_id.id)])
            if not analytic:
                analytic_obj = self.env['account.analytic.account'].create({
                    'partner_id':self.order_id.partner_id.id,
                    'name':self.order_id.partner_id.name,
                    'company_id':self.order_id.company_id.id,
                    'plan_id':plan.id,
                    })
                distribution = {str(analytic_obj.id):100.0}
                self.analytic_distribution = distribution
            elif analytic:
                analytic_plan = analytic.filtered(lambda r:r.plan_id.id == plan.id)
                if analytic_plan:
                    distribution = {str(analytic_plan.id):100.0}
                    self.analytic_distribution = distribution
        else:
            self.analytic_distribution = False

    """@api.depends() should contain all fields that will be used in the calculations"""

    @api.depends('working_days', 'working_hours', 'product_uom_qty', 'price_unit','total_add_monthly','working_month')
    def _compute_monthly_hours_rate(self):
            for rec in self:
                if rec.order_id.is_man_power_order == True:
                    rec.monthly_hours = rec.working_days.day * rec.working_hours.hours
                    rec.month_rate = rec.monthly_hours * rec.price_unit
                    rec.total_monthly = rec.month_rate * rec.product_uom_qty
                else:
                    return False

    @api.onchange('working_month')
    def _onchange_total_month(self):
        for rec in self:
            if rec.order_id.is_man_power_order == True:
                rec.update({'total_add_monthly': rec.total_monthly * rec.working_month.monthly})


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','total_add_monthly','working_days','working_hours')
    def _compute_amount(self):
        super (SaleOrderLineKeffah,self)._compute_amount()
        for line in self:
            if not line.order_id.is_man_power_order:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            else:
                price = (line.total_add_monthly / line.product_uom_qty)  * (1 - (line.discount or 0.0) / 100.0)

                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineKeffah, self)._prepare_invoice_line(**optional_values)
        res.update({
            'price_unit': self.price_subtotal / self.product_uom_qty,
            'quantity':self.product_uom_qty})
        return res





    






