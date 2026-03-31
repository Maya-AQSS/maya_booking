{
    'name': "Maya | Booking",
    'version': '19.0.1.0',

    'description': "Reserva de espacios, apoyos y préstamo de material",
    'long_description': """
        Este módulo permite la reserva de espacios, la solicitud de apoyos y el préstamo de material en la plataforma.
    """,

    'author': "Departamento de informática CEED",
    'website': "https://maya-aqss.github.io/maya_booking/",
    'maintainer': 'Alfredo Oltra <alfredo.ptcf@gmail.com>',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',

    'license': 'AGPL-3',
    'price': 0,

    # any module necessary for this one to work correctly
    'depends': ['base', 'maya_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/booking_type.xml',
    ],
    
    'installable': True,
    'application': False,
}

