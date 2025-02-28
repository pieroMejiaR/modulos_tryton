from trytond.pool import Pool
from .red_social import RedSocialChannel

def register():
    Pool.register(
        RedSocialChannel,
        module='redes_sociales', type_='model')