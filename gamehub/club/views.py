import datetime
from pathlib import Path
import json

from django.shortcuts import render
from django.http import Http404, HttpRequest, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.forms.models import model_to_dict
from django.views import View
from django.db.models.query import QuerySet

from club.models import Club, GalleryImage, Feedback, User, Booking


class HomepageView(View):
    homepage_template_name = "club/homepage.html"
    authpage_path_name = "authpage:authpage"

    def delete_user_login_info(self, request: HttpRequest):
        del request.session["remembered"]
        del request.session["username"]
        del request.session["password"]

    def get_averate_rounded_rating(self, club: Club) -> int:
        if len(club.feedbacks.all()) == 0:
            return 0

        total_rating = 0
        cnt_rating = 0

        for feedback in club.feedbacks.all():
            total_rating += int(feedback.rating)
            cnt_rating += 1

        return int(round(total_rating / cnt_rating))

    def get_clubs_data(self) -> dict:
        clubs = (
            Club
            .objects
            .all()
            .only(
                "name",
                "main_image",
                "price",
                "contact",
                "main_image",
                "feedbacks",
            )
            .select_related("contact", "main_image")
            .prefetch_related("feedbacks")
        )

        clubs_data = list()
        for club in clubs:
            rating = self.get_averate_rounded_rating(club)
            club_data = dict()
            club_data["name"] = club.name
            club_data["main_image"] = club.main_image
            club_data["full_star_inds"] = range(rating)
            club_data["empty_star_inds"] = range(5 - rating)
            club_data["contact"] = club.contact
            club_data["price"] = club.price
            club_data["pk"] = club.pk

            clubs_data.append(club_data)

        clubs_data.sort(key=lambda x: -len(list(x["full_star_inds"])))
        
        return {
            "clubs": clubs_data
        }

    def get_dropdown_menu(self) -> dict:
        return {
            "dropdown_content_options": [
                {
                    "text": "Мои записи",
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

    def handle_ajax(self, request: HttpRequest, context) -> JsonResponse:
        if request.POST.get("action") == "logout":
            self.delete_user_login_info(request)
            context["redirect_to"] = reverse(self.authpage_path_name)
            return JsonResponse(data=context)

        else:
            raise Exception("Cannot identify the purpose of ajax request")

    def get(self, request: HttpRequest):
        context = {}
        context.update(self.get_dropdown_menu())
        context.update(self.get_clubs_data())
        context.update({
            "username": request.session.get("username"),
        })
    
        return render(request, self.homepage_template_name, context)

    def post(self, request: HttpRequest):
        context = {}
        context.update(self.get_dropdown_menu())

        if "action" in request.POST:
            return self.handle_ajax(request, context)

        else:
            raise Exception("Cannot identify the purpose of POST request")


class BookingsView(View):
    my_bookings_template_name = "club/my_bookings.html"

    def delete_inactive_bookings(self, user: User):
        todays_date = datetime.date.today()
        Booking.objects.filter(date__lt=todays_date).delete()

    def get_dropdown_menu(self) -> dict:
        return {
            "dropdown_content_options": [
                {
                    "text": "Главная старница",
                    "button_id": "homepage-btn",
                    "img_name": "gamehub.png",
                },
                {
                    "text": "Выйти с аккаунта",
                    "button_id": "logout-btn",
                    "img_name": "logout.png",
                },
            ],
        }

    def get(self, request: HttpRequest):
        user = User.objects.get(username=request.session.get("username"))
    
        self.delete_inactive_bookings(user=user)

        bookings = (
            Booking
            .objects
            .filter(user=user)
            .select_related("club")
            .only(
                "date",
                "hours",
                "computer_order",
                "club__name",
            )
        )

        date_to_club_ids = dict()
        for booking in bookings:
            if booking.date not in date_to_club_ids:
                date_to_club_ids[booking.date] = set()
            date_to_club_ids[booking.date].add(booking.club.id)

        date_to_clubs = dict()
        for date, club_ids in date_to_club_ids.items():
            if date not in date_to_clubs:
                date_to_clubs[date] = list()
            for club_id in club_ids:
                date_to_clubs[date].extend([club for club in Club.objects.filter(pk=club_id)])
        
        date_to_clubs_list = [(date, date_to_clubs[date]) for date in date_to_clubs.keys()]
        date_to_clubs_list.sort()

        context = {
            "date_to_clubs": date_to_clubs_list,
            "username": request.session.get("username"),
        }
        context.update(self.get_dropdown_menu())
        return render(request, self.my_bookings_template_name, context)


class ClubDetailsView(View):
    club_details_template_name = "club/club_details.html"

    def get_clubs_queryset(self, pk: int):
        return (
            Club
            .objects
            .filter(pk=pk)
            .select_related("main_image", "contact")
            .prefetch_related("gallery_images", "feedbacks", "bookings")
        )

    def get_feedbacks_data(self, club: Club, pk: int) -> list:
        feedbacks_data = list()
        for feedback in club.feedbacks.all():
            feedback_data = {
                "name": feedback.name,
                "full_star_inds": range(feedback.rating),
                "empty_star_inds": range(5 - feedback.rating),
                "date": feedback.date,
                "text": feedback.text,
            }
            feedbacks_data.append(feedback_data)
        return feedbacks_data

    def get_dropdown_menu(self) -> dict:
        return {
            "dropdown_content_options": [
                {
                    "text": "Главная старница",
                    "button_id": "homepage-btn",
                    "img_name": "gamehub.png",
                },
                {
                    "text": "Мои записи",
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

    def get_rightside_image(self, request: HttpRequest, club):
        prev_image_url = request.POST.get("current_image_url")
            
        if club.main_image.image.url == prev_image_url:
            return prev_image_url

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
                return current_gallery_image.image.url
            else:
                return club.main_image.image.url

    def get_leftside_image(self, request: HttpRequest, club):
        prev_image_url = request.POST.get("current_image_url")

        if club.main_image.image.url == prev_image_url:
            current_gallery_image : GalleryImage = club.gallery_images.all().order_by('pk').first()
            return current_gallery_image.image.url

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
                return current_gallery_image.image.url
            else:
                return prev_gallery_image.image.url

    # Returns the time intervals, when at least one computer is free
    def get_free_time_intervals(self, request: HttpRequest, club) -> list:
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        day = int(request.POST.get("day"))
        date = datetime.date(year=year, month=month, day=day)
        
        bookings = club.bookings.all().filter(date=date)
        if len(bookings) == 0:
            return [(i, (i + 1) % 24) for i in range(24)]
        
        time_interval_to_computers_booked = dict()
        for booking in bookings:
            for time_interval in booking.hours:
                print("HERE1", time_interval_to_computers_booked)
                print("HERE2", tuple(time_interval))
                if tuple(time_interval) not in time_interval_to_computers_booked:
                    time_interval_to_computers_booked[tuple(time_interval)] = 0
                time_interval_to_computers_booked[tuple(time_interval)] += 1
        

        free_time_intervals = set([(i, (i + 1) % 24) for i in range(24)]) # time intervals, when there's at least one free computer
        for time_interval, computers_booked in time_interval_to_computers_booked:
            if computers_booked == club.number_of_computers:
                free_time_intervals.remove(time_interval)

        return sorted(list(free_time_intervals))

    def get_free_computer_orders(self, request: HttpRequest, club: Club) -> list:
        flatten_time_intervals = list(map(int, request.POST.getlist("time_intervals[]")))
        time_intervals = set(
            (
                flatten_time_intervals[i],
                flatten_time_intervals[i + 1]
            ) for i in range(0, len(flatten_time_intervals), 2)
        )
            
        free_computers = set(list(range(1, club.number_of_computers + 1)))
        bookings = club.bookings.all()
        for booking in bookings:
            if len(set(map(tuple, booking.hours)) & time_intervals) > 0:
                if booking.computer_order in free_computers:
                    free_computers.remove(booking.computer_order)

        return list(sorted(free_computers))

    def save_feedback(self, username: str, feedback_message: str, feedback_rating: int, club: Club):
        Feedback.objects.create(name=username, text=feedback_message, rating=feedback_rating, club=club)

    def save_booking(self, request: HttpRequest, club: Club, context: dict) -> list:
        flatten_time_intervals = list(map(int, request.POST.getlist("time_intervals[]")))
        time_intervals = set(
            (
                flatten_time_intervals[i],
                flatten_time_intervals[i + 1]
            ) for i in range(0, len(flatten_time_intervals), 2)
        )
        booking_year = int(request.POST.get("booking_year"))
        booking_month = int(request.POST.get("booking_month"))
        booking_day = int(request.POST.get("booking_day"))
        booking_date = datetime.date(year=booking_year, month=booking_month, day=booking_day)
        computer_orders = request.POST.getlist("computer_orders[]")

        user = User.objects.get(username=request.session.get("username"))
        early_bookings : QuerySet[Booking] = club.bookings.all().filter(date=booking_date, user=user)

        for computer_order in computer_orders:
            if early_booking := early_bookings.filter(computer_order=computer_order).first():
                if len(set(map(tuple, early_booking.hours)) & time_intervals) > 0:
                    context["has_error"] = True
                    context["error_message"] = f"Вы уже раннее забранировали место на это время"
                    return
                else:
                    early_booking.hours.extend(time_intervals)
                    early_booking.save()
            
            else:
                Booking.objects.create(date=booking_date, hours=list(time_intervals), computer_order=computer_order, club=club, user=user)

    def handle_ajax(self, request: HttpRequest, context: dict, club: Club) -> JsonResponse:
        if request.POST.get("action") == "get-left-image":
            context["current_image_url"] = self.get_rightside_image(request, club)
            return JsonResponse(data=context)

        elif request.POST.get("action") == "get-right-image":
            context["current_image_url"] = self.get_leftside_image(request, club)
            return JsonResponse(data=context)

        elif request.POST.get("action") == "save-feedback":
            self.save_feedback(request.session.get("username"), request.POST.get("feedback_message"), request.POST.get("feedback_rating"), club)
            return JsonResponse(data={})
        
        elif request.POST.get("action") == "save-date":
            free_time_intervals = self.get_free_time_intervals(request, club)
            context = {
                "time_intervals": free_time_intervals,
            }
            return JsonResponse(data=context)

        elif request.POST.get("action") == "get-free-computers":
            free_computers = self.get_free_computer_orders(request, club)
            context = {
                "computer_orders": free_computers,
            }
            return JsonResponse(data=context)

        elif request.POST.get("action") == "commit-booking":
            context = dict()
            self.save_booking(request, club, context)
            return JsonResponse(data=context)

        else:
            raise Exception("Cannot find the purpose of ajax request")

    def get(self, request: HttpRequest, pk: int):
        club = self.get_clubs_queryset(pk).first()
        feedbacks_data = self.get_feedbacks_data(club, pk)
        context = {
            "pk": club.pk,
            "club": club,
            "feedbacks": feedbacks_data,
            "main_image_url": club.main_image.image.url,
            "username": request.session.get("username"),
        }
        context.update(self.get_dropdown_menu())

        return render(request, self.club_details_template_name, context)

    def post(self, request: HttpRequest, pk: int):
        club = self.get_clubs_queryset(pk).first()
        context = {}
        
        if "action" in request.POST:
            return self.handle_ajax(request, context, club)
        else:
            raise Exception("Cannot identify the purpose of POST request")


class BookingDetails(View):
    my_booking_details_template_name = "club/my_booking_details.html"

    def get_dropdown_menu(self) -> dict:
        return {
            "dropdown_content_options": [
                {
                    "text": "Главная старница",
                    "button_id": "homepage-btn",
                    "img_name": "gamehub.png",
                },
                {
                    "text": "Мои записи",
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

    def get(self, request: HttpRequest, club_pk: int, date_str: str):
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        club = Club.objects.filter(pk=club_pk).select_related("contact").only("contact").first()

        bookings = list()
        for booking in Booking.objects.filter(club__id=club_pk, date=date):
            hours = sorted(booking.hours)
            time_intervals = list()
            for hour in hours:
                if len(time_intervals) == 0:
                    time_intervals.append((hour[0], hour[1]))
                else:
                    if time_intervals[-1][1] == hour[0]:
                        start_time = time_intervals[-1][0]
                        end_time = hour[1]
                        time_intervals.pop()
                        time_intervals.append((start_time, end_time))
                    else:
                        time_intervals.append(tuple(hour))
            
            time_intervals_str = " & ".join(
                [f"{time_interval[0]}:00-{time_interval[1]}:00" for time_interval in time_intervals]
            )

            bookings.append({
                "computer_order": booking.computer_order,
                "time_intervals": time_intervals_str,
            })
        
        bookings.sort(key=lambda dct: dct["computer_order"])

        context = {
            "club": club,
            "bookings": bookings,
            "username": request.session.get("username"),
        }
        context.update(self.get_dropdown_menu())

        return render(request, self.my_booking_details_template_name, context)
