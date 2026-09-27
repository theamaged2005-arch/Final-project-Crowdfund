from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Egyptian mobile numbers: 010/011/012/015 followed by 8 digits
egyptian_phone_validator = RegexValidator(
    regex=r'^(\+20|0)?1[0125][0-9]{8}$',
    message="Enter a valid Egyptian mobile number, e.g. 01012345678"
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[egyptian_phone_validator])
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    birthdate = models.DateField(blank=True, null=True)
    facebook_profile = models.URLField(blank=True)
    country = models.CharField(max_length=64, blank=True)

    is_activated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"