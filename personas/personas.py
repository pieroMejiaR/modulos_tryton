import re
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval, Bool

__all__ = ['Persona']

class Persona(ModelSQL, ModelView):
    "Persona"
    __name__ = 'personas.persona'
    _rec_name = 'apellido'

    nombre = fields.Char('Nombre(s)', required=True)
    apellido = fields.Char('Apellido(s)', required=True)
    correo = fields.Char('Correo Electrónico', required=True, states={'readonly': Bool(Eval('active'))})
    redes_sociales = fields.Selection([
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
    ], 'Red Social')
    enlace_perfil = fields.Char('Enlace del perfil', required=True)
    active = fields.Boolean('Activo', help="Indica si la persona está activa")

    @classmethod
    def validate(cls, records):
        super(Persona, cls).validate(records)
        for record in records:
            cls.check_email(record)

    @staticmethod
    def check_email(record):
        if record.correo:
            correo_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(correo_regex, record.correo):
                raise ValueError("Correo electrónico no válido")