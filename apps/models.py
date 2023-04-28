import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models, connection
from django.db.models import Model, CharField, FloatField, TextField, ImageField, ForeignKey, SET_NULL, F, \
    DateTimeField, OneToOneField, CASCADE
from faker import Faker

from django_orm_cookbook import settings


# Create your models here.

class Category(Model):
    name = CharField(max_length=255)


class Product(Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)
    description = TextField()
    price = FloatField()
    image = ImageField(upload_to='media', null=True, blank=True)
    category = ForeignKey('apps.Category', on_delete=SET_NULL, null=True)
    date = DateTimeField(auto_now_add=True, null=True)

    # agar databaseda hali yaratilmagan bo'lsa prouctni category_id categoryni id siga teng bo'lganini olib name ga 1 qo'shib ketaverad
    # har run qilganimizda
    def save(self, *args, **kwargs):
        if not self.pk:
            Category.objects.filter(pk=self.category_id).update(name=F('name') + 1)
        super().save(*args, **kwargs)


class Car(Model):
    name = CharField(max_length=255)
    price = FloatField()
    # birga bur bo'g'lsh uchun albatta category_id unique bo'lish kerak
    category = OneToOneField('apps.Category', on_delete=CASCADE, primary_key=True)

    # shu modelni truncate qilish faqat sqliteda ishlamaydi, postgresqlda ishlaydi
    # @classmethod
    # def truncate(cls):
    #     with connection.cursor() as cursor:
    #         cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(cls._meta.db_table))

    # so'rash kerak
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)


# class User(AbstractUser):
#     follower = models.ManyToManyField('auth.User', blank=True)


class Employee(models.Model):
    manager = models.ForeignKey('self', on_delete=models.CASCADE)

# OR

# class Employee(models.Model):
#     manager = models.ForeignKey("app.Employee", on_delete=models.CASCADE)
