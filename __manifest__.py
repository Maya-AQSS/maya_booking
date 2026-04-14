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
    'category': 'Productivity',
    'license': 'AGPL-3',
    'price': 0,
    'depends': ['base', 'maya_core', 'web_timeline'],
    'data': [
        'security/ir.model.access.csv',
        'views/booking_type.xml',
        'views/place_view.xml',
    ],
    'installable': True,
    'application': False,
}