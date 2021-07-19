import uuid
from django.db import models


class Pet(models.Model):
    class PetsChoices(models.Choices):
        dog = 'dog'
        cat = 'cat'

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=10, choices=PetsChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}, {self.age}, {self.type}'


class Photo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    file = models.ImageField(upload_to='photos/')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, to_field='uuid')
