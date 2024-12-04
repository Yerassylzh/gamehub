from django.core.validators import MinLengthValidator
from django.db import models

from core.models import AbstractImage
from club.validators import phone_number_validator


class Club(models.Model):
    name = models.CharField(
        verbose_name="название",
        name="name",
        max_length=255,
        help_text="Введите название компьютерного клуба",
    )

    description = models.TextField(
        verbose_name="описание клуба",
        name="description",
        help_text="Введите описание клуба",
    )

    price = models.CharField(
        verbose_name="цена",
        name="price",
        max_length=255,
        help_text="Опишите цену",
    )

    number_of_computers = models.PositiveSmallIntegerField(
        verbose_name="общее количество компьютеров",
        name="number_of_computers",
        help_text="Введите общее количество компьютеров",
    )


    class Meta:
        verbose_name = "клуб"
        verbose_name_plural = "клубы"


class Contact(models.Model):
    address = models.CharField(
        verbose_name="адрес",
        name="address",
        max_length=255,
        help_text="Введите адрес компьютерного клуба",
    )

    phone_number = models.CharField(
        verbose_name="номер телефона",
        name="phone_number",
        max_length=255,
        help_text="Введите номер телефона",
        validators=[
            phone_number_validator,
        ]
    )

    email = models.EmailField(
        verbose_name="электронная почта",
        name="email",
        help_text="Введите электронную почту",
    )

    club = models.OneToOneField(
        Club,
        on_delete=models.CASCADE,
        related_query_name="contact",
        related_name="contact"
    )

    class Meta:
        verbose_name = "контакты"
        verbose_name_plural = "контакты"


class Feedback(models.Model):
    name = models.CharField(
        verbose_name="Автор",
        name="name",
        max_length=255,
    )

    text = models.TextField(
        verbose_name="описание отзыва",
        name="text",
        help_text="Напишите свой отзыв",
    )

    rating = models.PositiveSmallIntegerField(
        verbose_name="оценка",
        name="rating",
        help_text="Оцените в пяти звездах",
    )

    date = models.DateField(
        verbose_name="дата написания отзыва",
        name="date",
        auto_now_add=True,
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_query_name="feedbacks",
        related_name="feedbacks",
    )

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"


class GalleryImage(AbstractImage):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_query_name="gallery_images",
        related_name="gallery_images",
    )

    class Meta:
        verbose_name = "допольнительное изображение"
        verbose_name_plural = "дополнительные изображения"


class MainImage(AbstractImage):
    club = models.OneToOneField(
        Club,
        on_delete=models.CASCADE,
        related_name="main_image",
        related_query_name="main_image",
    )

    class Meta:
        verbose_name = "главное изображение"
        verbose_name_plural = "главные изображения"


class User(models.Model):
    username = models.CharField(
        verbose_name="имя пользователя",
        name="username",
        max_length=255,
    )

    password = models.CharField(
        verbose_name="пароль",
        name="password",
        max_length=255,
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username


class Booking(models.Model):
    date = models.DateField(
        verbose_name="дата",
        name="date",
    )

    hours = models.JSONField(
        verbose_name="забронированные часы",
        name="hours",
    )

    computer_order = models.PositiveSmallIntegerField(
        verbose_name="номер компьютера",
        name="computer_order",
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="bookings",
        related_query_name="bookings",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        related_query_name="bookings",
    )

    class Meta:
        verbose_name = "бронирование"
        verbose_name_plural = "бронировании"
