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
{
    'name': 'All in One Dynamic Approvals Pro',
    'version': '16.0.1.0.0',
    'summary': '',
    'category': '',
    'maintainer': 'Keffah Solutions the Est. Information Technology and Communication',
    'company': 'Keffah Solutions the Est. Information Technology and Communication',
    'website': 'https://www.kascco.sa',
    'depends': ['base', 'base_automation', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/approval_sequence.xml',
        'views/approval.xml',
        'wizard/approval_reject_reason.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 299.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
