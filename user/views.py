# user/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import CustomUserCreationForm, LoginForm, UserProfileForm
from .models import CustomUser
from .tokens import account_activation_token


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Ative sua conta Growplant.'
            message = render_to_string('registration\\acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.success(request, 'Um email de confirmação foi enviado para seu email. Favor ativar seu email no link para fazer o login.')
            return redirect('login')
        else:
            # Se o formulário não for válido, verificamos se o erro é de e-mail duplicado para um usuário inativo
            email = request.POST.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_active:
                    email_b64 = urlsafe_base64_encode(force_bytes(user.email))
                    return redirect('resend_activation', emailb64=email_b64)
            except CustomUser.DoesNotExist:
                pass  # Se o usuário não existe, apenas deixamos a página recarregar com os erros do formulário
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration\\signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active:
            messages.info(request, 'Sua conta já foi ativada. Você pode fazer o login.')
        else:
            user.is_active = True
            user.save()
            messages.success(request, 'Sua conta foi ativada com sucesso! Agora você pode fazer o login.')
        return redirect('login')
    else:
        if user is not None:
            messages.error(request, 'O link de ativação expirou ou é inválido. Por favor, solicite um novo.')
            email_b64 = urlsafe_base64_encode(force_bytes(user.email))
            return redirect('resend_activation', emailb64=email_b64)
        else:
            messages.error(request, 'O link de ativação é inválido.')
            return redirect('login')


def resend_activation_view(request, emailb64):
    try:
        email = force_str(urlsafe_base64_decode(emailb64))
        user = CustomUser.objects.get(email=email)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return HttpResponseNotFound("Link inválido ou usuário não encontrado.")

    if user.is_active:
        messages.info(request, 'Sua conta já está ativa. Você pode fazer login.')
        return redirect('login')

    if request.method == 'POST':
        current_site = get_current_site(request)
        mail_subject = 'Ative sua conta Growplant.'
        message = render_to_string('registration\\acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        email_message = EmailMessage(mail_subject, message, to=[user.email])
        email_message.send()
        messages.success(request, 'Um novo e-mail de ativação foi enviado com sucesso.')
        return redirect('resend_activation', emailb64=emailb64)

    return render(request, 'registration\\resend_activation.html', {'email': user.email})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                user = None
            if user is not None and user.check_password(password):
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Login bem-sucedido! Bem-vindo(a) de volta, {user.email}.')
                    return redirect('home')
                else:
                    messages.error(request, 'Sua conta ainda não foi ativada. Por favor, verifique seu e-mail.')
            else:
                messages.error(request, 'E-mail ou senha inválidos. Por favor, tente novamente.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos corretamente.')
    else:
        form = LoginForm()
    return render(request, 'registration\\login.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


@login_required
def profile_display_view(request):
    """
    View para apenas EXIBIR as informações do perfil.
    """
    # O objeto 'user' já está disponível em templates de views protegidas
    return render(request, 'registration\\profile_display.html')


@login_required
def profile_edit_view(request):
    """
    View para EDITAR as informações do perfil.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            # Após salvar, redireciona de volta para a PÁGINA DE VISUALIZAÇÃO
            return redirect('profile_display')
    else:
        form = UserProfileForm(instance=request.user)

    # Renomeamos o template para ficar mais claro
    return render(request, 'registration\\profile_edit.html', {'form': form})