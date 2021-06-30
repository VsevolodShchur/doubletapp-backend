from .models import Pet, Photo
from .serializers import PetSerializer, PhotoSerializer, \
                         DeleteResponseDataSerializer
from .pagination import PetsLimitOffsetPagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status, generics
from django.db import IntegrityError
import uuid


class PetView(generics.ListAPIView,
              generics.CreateAPIView,
              generics.DestroyAPIView):
    queryset = Pet.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = PetSerializer

    class _ErrorMessages:
        bad_has_photos_param = 'Bad "has_photos" query param, ' \
                               'options: "true", "false".'
        pet_id_not_found = 'Pet with the matching ID was not found.'

    def get(self, request, **kwargs):
        str_has_photos = self.request.query_params.get('has_photos')
        if str_has_photos and str_has_photos not in ('true', 'false'):
            response_data = dict(
                detail=self._ErrorMessages.bad_has_photos_param)
            return Response(data=response_data,
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = queryset if page is None else page
        has_photos = str_has_photos is None or str_has_photos == 'true'
        serializer_context = {'has_photos': has_photos}
        serializer = self.get_serializer(data,
                                         many=True,
                                         context=serializer_context)
        response_data = {'count': len(serializer.data),
                         'items': serializer.data}
        return Response(data=response_data)

    def delete(self, request, **kwargs):
        str_uuids = request.data['ids']
        queryset = self.get_queryset()

        response = DeleteResponseData()
        for str_uuid in str_uuids:
            try:
                pet_uuid = uuid.UUID(str_uuid)
                pet = queryset.get(uuid=pet_uuid)
                pet.delete()
                # queryset.get(id=pet_uuid).delete()
            except Pet.DoesNotExist:
                response.append_error(str_uuid,
                                      self._ErrorMessages.pet_id_not_found)
            except Exception as e:
                response.append_error(str_uuid, str(e))
            else:
                response.deleted += 1
        serializer = DeleteResponseDataSerializer(response)
        return Response(data=serializer.data,
                        status=status.HTTP_204_NO_CONTENT)


class PhotoUploadView(generics.CreateAPIView,
                      generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = PhotoSerializer

    class _ErrorMessages:
        file_not_found = 'No file in request.'

    def post(self, request, **kwargs):
        if 'file' not in request.data:
            response_data = {'detail': self._ErrorMessages.file_not_found}
            return Response(data=response_data,
                            status=status.HTTP_400_BAD_REQUEST)

        file = request.data['file']
        pet_uuid = kwargs.get('pet_uuid')
        photo = Photo(file=file, pet_id=pet_uuid)
        try:
            photo.save()
        except IntegrityError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(photo, context={'request': request})
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)


class DeleteResponseData:
    def __init__(self):
        self.deleted = 0
        self.errors = []

    def append_error(self, id, error):
        self.errors.append({'id': id, 'error': error})
