{
    "name": 'Hr Contract Enhancements',
    "version": '1.0',
    "author": 'Einas Omer',
    "category": '',
    "depends": ['base', 'hr_contract'],
    "data": [
        'views/hr_contract_views.xml',
        'views/employee_views.xml',
        'views/res_config_settings_views.xml',
        'data/cron.xml',
    ],
    "application": True,
    'installable': True,
}
