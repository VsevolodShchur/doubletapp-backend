from .models import Pet, Photo
from .serializers import PetSerializer, PhotoSerializer, \
                         PetViewGetQueryParamsSerializer, \
                         DeleteResponseSerializer, \
                         ListResponseSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound
from rest_framework import status, generics, pagination, parsers
from django.db import IntegrityError
import uuid


class PetView(generics.ListAPIView,
              generics.CreateAPIView,
              generics.DestroyAPIView):
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = PetSerializer

    def get_queryset(self):
        has_photos_param = self.request.query_params.get('has_photos')
        if not has_photos_param:
            return Pet.objects.all()

        has_photos = has_photos_param == 'true'
        return Pet.objects.filter(photo__isnull=not has_photos)

    def list(self, request, **kwargs):
        qp = PetViewGetQueryParamsSerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page:
            queryset = page
        serializer = ListResponseSerializer(queryset, 
                                            model_serializer=PetSerializer,
                                            context={'request': request})
        return Response(data=serializer.data)

    def destroy(self, request, **kwargs):
        str_uuids = request.data['ids']
        response = DeleteResponse()
        for str_uuid in str_uuids:
            try:
                pet_uuid = uuid.UUID(str_uuid)
                Pet.objects.get(uuid=pet_uuid).delete()
            except Pet.DoesNotExist:
                response.append_error(str_uuid,
                                      'Pet with the matching ID was not found.')
            except Exception as e:
                response.append_error(str_uuid, str(e))
            else:
                response.deleted += 1
        serializer = DeleteResponseSerializer(response)
        return Response(data=serializer.data,
                        status=status.HTTP_204_NO_CONTENT)


class PhotoUploadView(generics.CreateAPIView,
                      generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    parser_classes = [parsers.MultiPartParser]
    serializer_class = PhotoSerializer

    def create(self, request, **kwargs):
        if 'file' not in request.data:
            raise ParseError(detail='No file in request.')

        file = request.data['file']
        pet_uuid = kwargs.get('pet_uuid')
        photo = Photo(file=file, pet_id=pet_uuid)
        try:
            photo.save()
        except IntegrityError:
            raise NotFound()

        serializer = self.get_serializer(photo)
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)


class DeleteResponse:
    def __init__(self):
        self.deleted = 0
        self.errors = []

    def append_error(self, id, error):
        self.errors.append({'id': id, 'error': error})
