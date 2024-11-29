from django.core.exceptions import ValidationError

class ValidateUsernameMinLength:
    def __init__(self, min_length):
        self.min_length = min_length

    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(
                f"Имя пользователя должно содержать минимум {self.min_length} символов."
            )
