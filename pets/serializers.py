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
        return f'http://{domain}{photo_path}'


class PetSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='uuid', read_only=True)
    photos = PhotoSerializer(source='photo_set', read_only=True, many=True)

    class Meta:
        model = Pet
        fields = ('id', 'name', 'age', 'type', 'photos', 'created_at',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not self.context.get('has_photos', False):
            representation.pop('photos')

        elif self.context.get('photos_as_url_list', False):
            photos = representation['photos']
            urls = [photo['url'] for photo in photos]
            representation['photos'] = urls

        return representation


class DeleteResponseDataSerializer(serializers.Serializer):
    deleted = serializers.IntegerField(read_only=True)
    errors = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )
