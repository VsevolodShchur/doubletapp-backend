from django.contrib.sites.models import Site
from rest_framework import serializers
from .models import Pet, Photo


class PhotoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='uuid')
    url = serializers.SerializerMethodField('get_photo_url')

    class Meta:
        model = Photo
        fields = ('id', 'url',)

    def get_photo_url(self, photo):
        photo_path = photo.file.url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(photo_path)

        domain = Site.objects.get_current().domain
        return f'https://{domain}{photo_path}'


class PetSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='uuid', read_only=True)
    photos = PhotoSerializer(source='photo_set', read_only=True, many=True)

    class Meta:
        model = Pet
        fields = ('id', 'name', 'age', 'type', 'photos', 'created_at',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        serializer_context = {'request': self.context.get('request')}
        self.fields['photos'].context.update(serializer_context)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if self.context.get('photos_as_url_list', False):
            photos = representation['photos']
            urls = [photo['url'] for photo in photos]
            representation['photos'] = urls

        return representation


class DeleteResponseSerializer(serializers.Serializer):
    deleted = serializers.IntegerField(read_only=True)
    errors = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )


class ListResponseSerializer(serializers.Serializer):
    count = serializers.SerializerMethodField('get_count')
    items = serializers.SerializerMethodField('get_items')

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop('model_serializer')
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_count(instance_list):
        return len(instance_list)

    def get_items(self, instance_list):
        serializer = self.serializer(instance_list, many=True, context=self.context)
        return serializer.data


class PetViewGetQueryParamsSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=0)
    offset = serializers.IntegerField(required=False, min_value=0)
    has_photos = serializers.BooleanField(required=False, allow_null=True,
                                          default=None)
