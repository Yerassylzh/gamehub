from django.forms import CharField, Form, TextInput, CheckboxInput, BooleanField

from authpage.validators import ValidateUsernameMinLength

class AuthForm(Form):
    username = CharField(
        widget=TextInput(
            attrs={
                "placeholder": "Имя пользователя",
                "class": "input-field",
                "type": "text",
                "id": "username",
            }
        ),
        validators=[
            ValidateUsernameMinLength(10),
        ]
    )

    password = CharField(
        max_length=255,
        widget=TextInput(
            attrs={
                "placeholder": "Пароль",
                "class": "input-field",
                "type": "password",
                "id": "password",
            }
        )
    )

    remember_me = BooleanField(
        widget=CheckboxInput(
            attrs={
                "type": "checkbox",
                "class": "remember-me",
                "id": "remember-me",
            },
        ),
        label="Запомнить меня на месяц",
        required=False,
    )
