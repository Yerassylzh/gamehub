import hashlib

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.middleware.csrf import get_token

from authpage.forms import AuthForm
from club.models import User

LOGIN_OPTION = 0
SIGNUP_OPTION = 1
current_auth_option = LOGIN_OPTION


def get_password_hash(password: str) -> str:
    h = hashlib.new("SHA256")
    h.update(password.encode())
    return h.hexdigest()


def set_any_auth_error(form: AuthForm, auth_errors: list, context: dict) -> str:
    if len(form.errors) > 0:
        errors_data = form.errors.as_data()
        error_data = errors_data[
            list(
                errors_data.keys()
            )[0] # Рандомный ключ
        ][0]  # берет лишь одну ошибку для красивого отображения
        context["error_message"] = error_data.messages[0]
        context["has_error_message"] = True

    elif len(auth_errors) > 0:
        context["error_message"] = auth_errors[0]
        context["has_error_message"] = True

    else:
        return None


def save_user_login_info(request: HttpRequest, username: str, password: str, remember_me=False) -> None:
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


def auth(request: HttpRequest) -> HttpResponse:
    global current_auth_option

    form = AuthForm()
    context = {
        "main_text": "ВХОД",
        "button_text": "Продолжить",
        "auth_option": current_auth_option,
        "csrf_token": get_token(request),
    }
    
    auth_errors = []
    if request.POST.get("action", "none") == "change-auth-type":
        if request.POST.get("auth-type", "none") == "login":
            context["auth_option"] = LOGIN_OPTION
            current_auth_option = LOGIN_OPTION
            return JsonResponse(data=context)

        elif request.POST.get("auth-type", "none") == "signup":
            context["auth_option"] = SIGNUP_OPTION
            current_auth_option = SIGNUP_OPTION
            return JsonResponse(data=context)

        else:
            raise Exception("Got error while changing an auth type")

    elif request.POST.get("action", "none") == "auth-user":
        if current_auth_option == LOGIN_OPTION:
            form = AuthForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"].strip()
                password = form.cleaned_data["password"].strip()
                password_hash = get_password_hash(password)
                remember_me = form.cleaned_data["remember_me"]
                if len(User.objects.filter(username=username, password=password_hash)) > 0:
                    context["success"] = True
                    context["redirect_to"] = reverse("club:homepage")
                    save_user_login_info(request, username, password, remember_me)
                    return JsonResponse(data=context)

                elif len(User.objects.filter(username=username)) > 0:
                    auth_errors.append("Неверный пароль")

                else:
                    auth_errors.append("Пользователь не найден")

                set_any_auth_error(form, auth_errors, context)
                return JsonResponse(data=context)

            else:
                set_any_auth_error(form, auth_errors, context)
                return JsonResponse(data=context)

        elif current_auth_option == SIGNUP_OPTION:
            form = AuthForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data["username"].strip()
                password = form.cleaned_data["password"].strip()
                password_hash = get_password_hash(password)
                remember_me = form.cleaned_data["remember_me"]

                if len(User.objects.filter(username=username)) > 0:
                    auth_errors.append("Пользователь с таким именем уже существует.")
                    set_any_auth_error(form, auth_errors, context)
                    return JsonResponse(data=context)

                else:
                    User.objects.create(username=username, password=password_hash)
                    context["success"] = True
                    context["redirect_to"] = reverse("club:homepage")
                    save_user_login_info(request, username, password, remember_me)
                    return JsonResponse(data=context)
            
            else:
                set_any_auth_error(form, auth_errors, context)
                return JsonResponse(data=context)

        context["form"] = form

        return JsonResponse(data=context)

    elif "remembered" in request.session:
        return redirect(reverse("club:homepage"))

    else:

        form = AuthForm()
        context["form"] = form

        return render(request, "authpage/authpage.html", context=context)
