# user/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Importe o nosso novo gerenciador
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    username = None  # Removemos o campo username
    email = models.EmailField(_('email address'), unique=True)

    # Definimos que o campo de login agora é o email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # O e-mail e a senha são obrigatórios por padrão

    # Dizemos ao CustomUser para usar nosso CustomUserManager
    objects = CustomUserManager()

    def __str__(self):
        return self.email