from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser
from django import forms

class CustomUserCreationForm(UserCreationForm):
    # Sobrescrevemos o campo 'email' para adicionar nosso placeholder e outras customizações.
    email = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Digite seu e-mail'})
    )

    # O UserCreationForm usa 'password1' e 'password2' internamente.
    # Nós os sobrescrevemos para adicionar placeholders e mudar os rótulos.
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Crie uma senha forte'})
    )
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirme sua senha'})
    )
    class Meta:
        model = CustomUser
        fields = ('email',)

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu-email@exemplo.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'})
    )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Digite o e-mail da sua conta'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    # O SetPasswordForm usa 'new_password1' e 'new_password2'
    new_password1 = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Digite sua nova senha'})
    )
    new_password2 = forms.CharField(
        label="Confirmação da Nova Senha",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirme sua nova senha'})
    )

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        required=False, # O nome não é obrigatório
        widget=forms.TextInput(attrs={'placeholder': 'Seu primeiro nome'})
    )
    last_name = forms.CharField(
        label="Sobrenome",
        max_length=150,
        required=False, # O sobrenome não é obrigatório
        widget=forms.TextInput(attrs={'placeholder': 'Seu sobrenome'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')