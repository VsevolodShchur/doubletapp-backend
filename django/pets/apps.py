from django.apps import AppConfig


class PetsAppConfig(AppConfig):
    name = 'pets'

    def ready(self):
        import pets.signals
