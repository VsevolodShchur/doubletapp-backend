from .models import Pet
from .serializers import PetSerializer
from .pagination import PetsLimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status, generics


class PetView(generics.CreateAPIView):
    queryset = Pet.objects.all()
    pagination_class = PetsLimitOffsetPagination
    serializer_class = PetSerializer

    def get(self, request, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = queryset if page is None else page
        serializer = self.get_serializer(data, many=True)
        response_obj = {'count': len(serializer.data),
                        'items': serializer.data}
        return Response(response_obj)

    def delete(self, request):
        all_pets = self.get_queryset()
        ids = [pet.id for pet in all_pets]
        all_pets.delete()
        response_obj = {'ids': ids}
        return Response(data=response_obj, status=status.HTTP_204_NO_CONTENT)
