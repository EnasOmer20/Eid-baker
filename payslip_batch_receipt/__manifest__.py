
{
    'name': 'Payslip Batch Receipt',
    'version': '1.0',
    'summary': 'Create a payslip receipt when validating payslip batches',
    'category': 'Payroll',
    'author': 'Einas Omer',
    'depends': ['om_hr_payroll_account', 'account'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

