from pathlib import Path
import json

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.forms.models import model_to_dict

from club.models import Club, GalleryImage


def logout(request: HttpRequest):
    del request.session["remembered"]
    del request.session["username"]
    del request.session["password"]


def get_averate_rounded_rating(club: Club) -> int:
    if len(club.feedbacks.all()) == 0:
        return 0

    total_rating = 0
    cnt_rating = 0

    for feedback in club.feedbacks.all():
        total_rating += int(feedback.rating)
        cnt_rating += 1

    return int(round(total_rating / cnt_rating))


def home(request: HttpRequest):
    context = {
        "dropdown_content_options": [
            {
                "text": "Запись",
                "button_id": "my-bookings",
                "img_name": "gamepad.png",
            },
            {
                "text": "Выйти с аккаунта",
                "button_id": "logout-btn",
                "img_name": "logout.png",
            },
        ]
    }

    if "action" in request.POST:
        if request.POST.get("action") == "logout":
            logout(request)
            context["redirect_to"] = reverse("authpage:authpage")
            return JsonResponse(data=context)
        else:
            raise Exception("invalid action")

    else:
        clubs = (
            Club
            .objects
            .all()
            .only(
                "name",
                "main_image",
                "contact",
                "price",
            )
            .select_related("contact", "main_image")
            .prefetch_related("feedbacks")
        )

        clubs_data = list()
        for club in clubs:
            rating = get_averate_rounded_rating(club)
            club_data = dict()
            club_data["name"] = club.name
            club_data["main_image"] = club.main_image
            club_data["full_star_inds"] = range(rating)
            club_data["empty_star_inds"] = range(5 - rating)
            club_data["contact"] = club.contact
            club_data["price"] = club.price
            club_data["pk"] = club.pk

            clubs_data.append(club_data)

        context.update({
            "clubs": clubs_data,
            "username": request.session.get("username"),
        })

        return render(request, "club/homepage.html", context)


def bookings(request: HttpRequest):
    pass


def club_details(request: HttpRequest, pk: int):
    club_queryset = (
        Club
        .objects
        .filter(pk=pk)
        .select_related("main_image")
        .prefetch_related("gallery_images")
    )
    club = club_queryset.first()

    feedbacks_data = list()
    for feedback in club.feedbacks.all():
        feedback_data = {
            "name": feedback.name,
            "full_star_inds": feedback.rating,
            "empty_star_inds": 5 - feedback.rating,
            "date": feedback.date,
            "text": feedback.text,
        }

        feedbacks_data.append(feedback_data)

    context = {
        "pk": club.pk,
        "club": model_to_dict(club),
        "feedbacks": feedbacks_data,
        "main_image_url": club.main_image.image.url,
        "username": request.session.get("username"),
        "dropdown_content_options": [
            {
                "text": "Главная старница",
                "button_id": "homepage-btn",
                "img_name": "gamehub.png",
            },
            {
                "text": "Запись",
                "button_id": "my-bookings",
                "img_name": "gamepad.png",
            },
            {
                "text": "Выйти с аккаунта",
                "button_id": "logout-btn",
                "img_name": "logout.png",
            },
        ],
    }

    if "action" in request.POST:
        if request.POST.get("action") == "get-left-image":
            prev_image_url = request.POST.get("current_image_url")
            
            if club.main_image.image.url == prev_image_url:
                context["current_image_url"] = prev_image_url
                return JsonResponse(data=context)

            else:
                prev_gallery_image : GalleryImage = (
                    club
                    .gallery_images
                    .all()
                    .filter(
                        image=(
                            prev_image_url
                            .replace(settings.MEDIA_URL, '')
                        )
                    ).first()
                )
                current_gallery_image : GalleryImage = club.gallery_images.all().filter(pk__lt=prev_gallery_image.pk).order_by('-pk').first()
                
                if current_gallery_image:
                    context["current_image_url"] = current_gallery_image.image.url
                else:
                    context["current_image_url"] = club.main_image.image.url
                return JsonResponse(data=context)
        
        elif request.POST.get("action") == "get-right-image":
            prev_image_url = request.POST.get("current_image_url")

            if club.main_image.image.url == prev_image_url:
                current_gallery_image : GalleryImage = club.gallery_images.all().order_by('pk').first()
                context["current_image_url"] = current_gallery_image.image.url
                return JsonResponse(data=context)

            else:
                prev_gallery_image : GalleryImage = (
                    club
                    .gallery_images
                    .all()
                    .filter(
                        image=(
                            prev_image_url
                            .replace(settings.MEDIA_URL, '')
                        )
                    ).first()
                )
                current_gallery_image : GalleryImage = club.gallery_images.all().filter(pk__gt=prev_gallery_image.pk).order_by('pk').first()

                if current_gallery_image:
                    context["current_image_url"] = current_gallery_image.image.url
                else:
                    context["current_image_url"] = prev_gallery_image.image.url
                return JsonResponse(data=context)

        else:
            raise Exception("Invalid action option")

    else:
        return render(request, "club/club_details.html", context)
