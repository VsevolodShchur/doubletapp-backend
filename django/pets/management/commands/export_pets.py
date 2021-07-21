from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer
from pets.models import Pet
from pets.serializers import PetSerializer


class Command(BaseCommand):
    """
    Команда выгрузки питомцев
    """
    help = 'Export pets data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--has_photos',
            choices=['true', 'false'],
            help='Filter data; true=export pets with photos, false=export pets without photos',
        )

    def handle(self, *args, **options):
        has_photos = options['has_photos']

        pets_data = Pet.objects.all()
        if has_photos:
            pets_data = pets_data.filter(photo__isnull=has_photos != 'true')

        serializer = PetSerializer(pets_data,
                                   many=True,
                                   context={'photos_as_url_list': True})
        content = JSONRenderer().render({'pets': serializer.data},
                                        renderer_context={'indent': 4})
        self.stdout.write(content.decode('utf-8'))
