from rest_framework.pagination import LimitOffsetPagination


class PetsLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    offset = 0
