from .models import Pet, Photo
from .serializers import PetSerializer, PhotoSerializer, \
                         PetViewListQueryParamsSerializer, \
                         DestroyResponseSerializer, \
                         ListResponseSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound
from rest_framework import status, generics, pagination, parsers
from django.core.exceptions import ValidationError


class PetView(generics.ListAPIView,
              generics.CreateAPIView,
              generics.DestroyAPIView):
    """
    View на получение списка, создание и удаление питомцев
    """
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = PetSerializer

    def get_queryset(self):
        has_photos_param = self.request.query_params.get('has_photos')
        if not has_photos_param:
            return Pet.objects.all()

        has_photos = has_photos_param == 'true'
        return Pet.objects.filter(photo__isnull=not has_photos)

    def list(self, request, **kwargs):
        qp = PetViewListQueryParamsSerializer(data=request.query_params)
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
        uuids = request.data['ids']
        response = DestroyResponse()
        for pet_uuid in uuids:
            try:
                pet = Pet.objects.get(uuid=pet_uuid)
            except Pet.DoesNotExist:
                response.append_error(pet_uuid, 'Pet with the matching ID was not found.')
            except ValidationError as e:
                response.append_error(pet_uuid, e.message % {'value': pet_uuid})
            else:
                pet.delete()
                response.deleted += 1
        serializer = DestroyResponseSerializer(response)
        return Response(data=serializer.data)


class PhotoView(generics.CreateAPIView,
                generics.RetrieveAPIView):
    """
    View на загрузку и получение фотографий питомцев
    """
    queryset = Photo.objects.all()
    parser_classes = [parsers.MultiPartParser]
    serializer_class = PhotoSerializer

    def create(self, request, **kwargs):
        if 'file' not in request.data:
            raise ParseError(detail='No file in request.')

        file = request.data['file']
        pet_uuid = kwargs.get('pet_uuid')
        try:
            Pet.objects.get(uuid=pet_uuid)
        except Pet.DoesNotExist:
            raise NotFound()
        photo = Photo(file=file, pet_id=pet_uuid)
        photo.save()
        serializer = self.get_serializer(photo)
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)


class DestroyResponse:
    """
    Ответ на запрос удаления списка объектов
    """
    def __init__(self):
        self.deleted = 0
        self.errors = []

    def append_error(self, id, error):
        self.errors.append({'id': id, 'error': error})
