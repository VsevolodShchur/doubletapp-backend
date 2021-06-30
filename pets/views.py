from .models import Pet, Photo
from .serializers import PetSerializer, PhotoSerializer, \
                         PetViewGetQueryParamsSerializer, \
                         DeleteResponseDataSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ParseError, NotFound
from rest_framework import status, generics
from django.db import IntegrityError
import uuid


class PetView(generics.ListAPIView,
              generics.CreateAPIView,
              generics.DestroyAPIView):
    queryset = Pet.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = PetSerializer

    def get(self, request, **kwargs):
        qp = PetViewGetQueryParamsSerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = queryset if page is None else page

        serializer_context = {'has_photos': qp.validated_data['has_photos']}
        serializer = self.get_serializer(data,
                                         many=True,
                                         context=serializer_context)
        response_data = {'count': len(serializer.data),
                         'items': serializer.data}
        return Response(data=response_data)

    def delete(self, request, **kwargs):
        str_uuids = request.data['ids']
        queryset = self.get_queryset()

        response_data = DeleteResponseData()
        for str_uuid in str_uuids:
            try:
                pet_uuid = uuid.UUID(str_uuid)
                queryset.get(uuid=pet_uuid).delete()
            except Pet.DoesNotExist:
                response_data.append_error(str_uuid,
                                           'Pet with the matching ID was not found.')
            except Exception as e:
                response_data.append_error(str_uuid, str(e))
            else:
                response_data.deleted += 1
        serializer = DeleteResponseDataSerializer(response_data)
        return Response(data=serializer.data,
                        status=status.HTTP_204_NO_CONTENT)


class PhotoUploadView(generics.CreateAPIView,
                      generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = PhotoSerializer

    def post(self, request, **kwargs):
        if 'file' not in request.data:
            raise ParseError(detail='No file in request.')

        file = request.data['file']
        pet_uuid = kwargs.get('pet_uuid')
        photo = Photo(file=file, pet_id=pet_uuid)
        try:
            photo.save()
        except IntegrityError:
            raise NotFound()

        serializer = self.get_serializer(photo, context={'request': request})
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)


class DeleteResponseData:
    def __init__(self):
        self.deleted = 0
        self.errors = []

    def append_error(self, id, error):
        self.errors.append({'id': id, 'error': error})
