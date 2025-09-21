from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Novas URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-activation/<str:emailb64>/', views.resend_activation_view, name='resend_activation'),

    path('profile/', views.profile_display_view, name='profile_display'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration\\password_change_form.html',
             success_url='/user/password_change/done/'  # URL para redirecionar após sucesso
         ),
         name='password_change'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration\\password_change_done.html'
         ),
         name='password_change_done'),

    # --- URLs PARA REDEFINIÇÃO DE SENHA ---

    # 1. Página para solicitar a redefinição de senha (onde o usuário digita o e-mail)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='registration\\password_reset_form.html', form_class=CustomPasswordResetForm),
         name='password_reset'),

    # 2. Página de sucesso após o envio do e-mail de redefinição
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration\\password_reset_done.html'),
         name='password_reset_done'),

    # 3. O link enviado por e-mail, que leva à página para digitar a nova senha
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration\\password_reset_confirm.html', form_class=CustomSetPasswordForm),
         name='password_reset_confirm'),

    # 4. Página de sucesso após a senha ter sido redefinida
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration\\password_reset_complete.html'),
         name='password_reset_complete'),
]