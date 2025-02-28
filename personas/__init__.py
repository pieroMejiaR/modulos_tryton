from trytond.pool import Pool
from .personas import *

def register():
    Pool.register(
        Persona,
        module='personas', type_='model')