from django.apps import AppConfig


class PollsConfig(AppConfig):
    """ Poll config. """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
