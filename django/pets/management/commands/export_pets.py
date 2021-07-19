from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer
from pets.models import Pet
from pets.serializers import PetSerializer


class Command(BaseCommand):
    help = 'Export pets data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--has-photos',
            action='store_true',
            help='Include photos',
        )

    def handle(self, *args, **options):
        serializer_context = {
            'has_photos': options['has-photos'],
            'photos_as_url_list': True
        }
        serializer = PetSerializer(Pet.objects.all(),
                                   many=True,
                                   context=serializer_context)
        content = JSONRenderer().render({'pets': serializer.data},
                                        renderer_context={'indent': 4})
        self.stdout.write(content.decode('utf-8'))
