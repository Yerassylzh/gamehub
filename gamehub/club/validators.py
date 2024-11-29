from django.core.exceptions import ValidationError


def phone_number_validator(phone: str):
    filtered = list(filter(lambda c: '0' <= c <= '9', phone))
    if len(filtered) != 11:
        return ValidationError(
            "Не допустимый номер телефона",
        )
