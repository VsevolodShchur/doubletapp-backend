import uuid
from django.db import models


class Pet(models.Model):
    class Pets(models.Choices):
        dog = 'dog'
        cat = 'cat'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=10, choices=Pets.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}, {self.age}, {self.type}'


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.ImageField(upload_to='photos/')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
