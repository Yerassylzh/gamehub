import hashlib

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.middleware.csrf import get_token
from django.views import View

from authpage.forms import AuthForm
from club.models import User


class AuthpageView(View):
    auth_form_class = AuthForm
    authpage_template_url = "authpage/authpage.html"
    homepage_url_name = "club:homepage"

    LOGIN_OPTION = "0"
    SIGNUP_OPTION = "1"

    def get_password_hash(self, password: str) -> str:
        h = hashlib.new("SHA256")
        h.update(password.encode())
        return h.hexdigest()

    def set_any_auth_error(self, form: auth_form_class, auth_errors: list, context: dict) -> str:
        if len(form.errors) > 0:
            errors_data = form.errors.as_data()
            error_data = errors_data[
                list(
                    errors_data.keys()
                )[0]
            ][0]
            context["error_message"] = error_data.messages[0]
            context["has_error_message"] = True

        elif len(auth_errors) > 0:
            context["error_message"] = auth_errors[0]
            context["has_error_message"] = True

        else:
            return None

    def save_user_login_info(self, request: HttpRequest, username: str, password: str, remember_me=False) -> None:
        if remember_me:
            request.session.update({
                "remembered": True,
            })
            request.session.set_expiry(30 * 24 * 60 * 60)  # for an entire month
        else:
            request.session.set_expiry(0)

        request.session.update({
            "username": username,
            "password": password,
        })

    def login_user(self, request: HttpRequest, context) -> JsonResponse:
        auth_errors = []
        form = self.auth_form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"].strip()
            password_hash = self.get_password_hash(password)
            remember_me = form.cleaned_data["remember_me"]
            if len(User.objects.filter(username=username, password=password_hash)) > 0:
                context["success"] = True
                context["redirect_to"] = reverse(self.homepage_url_name)
                self.save_user_login_info(request, username, password, remember_me)
                return JsonResponse(data=context)

            elif len(User.objects.filter(username=username)) > 0:
                auth_errors.append("Неверный пароль")

            else:
                auth_errors.append("Пользователь не найден")

            self.set_any_auth_error(form, auth_errors, context)
            return JsonResponse(data=context)

        else:
            self.set_any_auth_error(form, auth_errors, context)
            return JsonResponse(data=context)

    def register_user(self, request: HttpRequest, context) -> JsonResponse:
        auth_errors = []
        form = self.auth_form_class(request.POST)
    
        if form.is_valid():
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"].strip()
            password_hash = self.get_password_hash(password)
            remember_me = form.cleaned_data["remember_me"]

            if len(User.objects.filter(username=username)) > 0:
                auth_errors.append("Пользователь с таким именем уже существует.")
                self.set_any_auth_error(form, auth_errors, context)
                return JsonResponse(data=context)

            else:
                User.objects.create(username=username, password=password_hash)
                context["success"] = True
                context["redirect_to"] = reverse(self.homepage_url_name)
                self.save_user_login_info(request, username, password, remember_me)
                return JsonResponse(data=context)
        
        else:
            self.set_any_auth_error(form, auth_errors, context)
            return JsonResponse(data=context)

    def auth_user(self, request: HttpRequest, context) -> JsonResponse:
        if request.POST.get("auth_type") == self.LOGIN_OPTION:
            return self.login_user(request, context)

        elif request.POST.get("auth_type") == self.SIGNUP_OPTION:
            return self.register_user(request, context)

        else:
            return Http404("Called 'auth_user' function but cannot identify the auth type")

    def handle_ajax(self, request: HttpRequest, context) -> JsonResponse:
        if request.POST.get("action") == "auth-user":
            return self.auth_user(request, context)
        
        else:
            return Http404("Cannot identify the purpose of ajax request")

    def get(self, request: HttpRequest):
        context = {
            "button_text": "Продолжить",
            "csrf_token": get_token(request),
        }

        if "remembered" in request.session:
            return redirect(reverse(self.homepage_url_name))
        else:
            form = self.auth_form_class()
            context["form"] = form
    
            return render(request, self.authpage_template_url, context)

    def post(self, request: HttpRequest):
        context = {
            "csrf_token": get_token(request),
        }

        if "action" in request.POST:
            return self.handle_ajax(request, context)

        else:
            return Http404("Cannot identify the purpose of POST request")
