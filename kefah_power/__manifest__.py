# -*- coding: utf-8 -*-
{
    'name': "Kefah Power",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "TIE",
    'website': "http://www.kascco.com",
    'category': 'Uncategorized',
    'version': '16.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_accounting_kit', 'analytic', 'sale', 'sale_management', 'hr', 'purchase', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/sale_order.xml',
        'views/account.xml',
        'views/res_partner.xml',
        'views/purchase.xml',
        'data/data.xml',
    ],
}
