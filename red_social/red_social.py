from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta
from trytond.model import ModelView
import requests
import logging

logger = logging.getLogger(__name__)

__all__ = ['RedSocialChannel']

API_KEY = 'API-KEY'

class RedSocialChannel(ModelSQL, ModelView):
    """Modelo para gestionar los canales de redes sociales"""
    
    __name__ = 'redes_sociales.channel'

    empresa = fields.Char('Empresa', required=True)
    username = fields.Char('Nombre del Canal', required=True)
    channel_id = fields.Char('ID del Canal', readonly=True)
    subscribers = fields.Integer('Suscriptores', readonly=True)
    videos = fields.Integer('Videos', readonly=True)
    latest_video = fields.Char('Último Video', readonly=True)
    video_url = fields.Char('URL del Último Video', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'obtener_datos': {},
        })

    @classmethod
    def obtener_datos(cls, records):
        """Obtiene los datos del canal de YouTube y los guarda en Tryton"""
        for record in records:
            if not record.username:
                continue

            # Obtener channel_id a partir del nombre de usuario
            channel_id = cls.get_channel_id(record.username)
            if not channel_id:
                logger.error(f"No se encontró el canal: {record.username}")
                continue
            record.channel_id = channel_id

            # Obtener estadísticas del canal
            stats = cls.fetch_youtube(channel_id)
            if stats:
                record.subscribers = stats.get('subscribers', 0)
                record.videos = stats.get('videos', 0)

            # Obtener información del último video
            video_data = cls.fetch_latest_video(channel_id)
            if video_data:
                record.latest_video = video_data.get('title', '')
                record.video_url = video_data.get('url', '')

            # Guardar cambios
            record.save()

    @staticmethod
    def get_channel_id(channel_name):
        """Obtiene el ID del canal a partir del nombre"""
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                return data['items'][0]['id']['channelId']
        return None

    @staticmethod
    def fetch_youtube(channel_id):
        """Obtiene estadísticas del canal"""
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                stats = data['items'][0]['statistics']
                return {
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'videos': int(stats.get('videoCount', 0)),
                }
        return None

    @staticmethod
    def fetch_latest_video(channel_id):
        """Obtiene el último video del canal"""
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&order=date&maxResults=1&type=video&key={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                video = data['items'][0]['snippet']
                video_id = data['items'][0]['id']['videoId']
                return {
                    'title': video['title'],
                    'date': video['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                }   
        return None