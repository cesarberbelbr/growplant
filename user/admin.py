# user/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Define a interface de administração para o modelo CustomUser.
    """
    # Usa o e-mail e a senha no formulário de criação de usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'), # password2 é para o campo de confirmação
        }),
    )
    # Mostra estes campos ao editar um usuário existente
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Campos que serão exibidos na lista de usuários
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    # Adiciona a capacidade de filtrar usuários por estes campos
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Adiciona uma barra de pesquisa que procura por estes campos
    search_fields = ('email', 'first_name', 'last_name')
    # Define a ordem padrão dos usuários na lista
    ordering = ('email',)
    # Define o campo usado para o login no admin e como username
    USERNAME_FIELD = 'email'

# Registra o nosso modelo CustomUser com a nossa classe de admin personalizada
admin.site.register(CustomUser, CustomUserAdmin)