# -*- encoding: utf-8 -*-

{
    "name": "Advances",
    "version": "1",
    "author": "IT-SYS Corporation --> Eman Ahmed",
    "category": "",
    'website': 'www.it-syscorp.com',
    'depends': ['base','hr','portal', 'utm','hr_contract','hr_payroll','update_input_path'],
    "summary": "Advances",
    'description': """
    """,
    "wbs":"BGM-32",

    "data": [
              'security/ir.model.access.csv',
              'security/security.xml',
             'sequence/sequence.xml',
             'views/advance_departments_view.xml',
             'views/employee_advance_view.xml',
              'sequence/salary_rule.xml'


    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    'price': 1,
    'currency': 'EUR',
    'license': 'AGPL-3',

}
