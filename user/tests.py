# user/tests.py

import re
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from .tokens import account_activation_token

# Pega o nosso modelo de usuário personalizado
CustomUser = get_user_model()


class TestCustomUserModel(TestCase):

    def test_create_user_successfully(self):
        """ Testa a criação de um usuário padrão com sucesso. """
        user = CustomUser.objects.create_user(email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass

    def test_create_user_with_no_email_raises_error(self):
        """ Testa se um erro é levantado ao criar usuário sem e-mail. """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email='', password='foo')

    def test_create_superuser_successfully(self):
        """ Testa a criação de um superusuário com sucesso. """
        admin_user = CustomUser.objects.create_superuser(email='super@user.com', password='foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """ Testa se um erro é levantado ao criar superusuário com is_staff=False. """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email='super@user.com', password='foo', is_staff=False)

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """ Testa se um erro é levantado ao criar superusuário com is_superuser=False. """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)


class TestSignupView(TestCase):

    def setUp(self):
        """ Garante que a caixa de e-mails de teste esteja limpa antes de cada teste. """
        mail.outbox = []

    def test_signup_page_loads_correctly(self):
        """ Testa se a página de signup carrega corretamente (GET). """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration\\signup.html')

    def test_successful_signup_creates_inactive_user_and_sends_email(self):
        """ Testa se um registro bem-sucedido cria um usuário inativo e envia e-mail. """
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.first()
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(b'Por favor, confirme seu endere', response.content)

    def test_signup_with_existing_active_user_fails(self):
        """ Testa se o registro falha se o e-mail já existir para um usuário ATIVO. """
        CustomUser.objects.create_user(email='test@example.com', password='somepassword', is_active=True)
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(response.context['form'].is_valid())

    def test_signup_with_existing_inactive_user_redirects(self):
        """
        Testa se o registro com um e-mail inativo existente redireciona
        para a página de reenvio de ativação.
        """
        inactive_email = 'inactive.user@test.com'
        CustomUser.objects.create_user(email=inactive_email, password='somepassword', is_active=False)
        form_data = {
            'email': inactive_email,
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }
        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(response.status_code, 302)
        email_b64 = urlsafe_base64_encode(force_bytes(inactive_email))
        expected_url = reverse('resend_activation', kwargs={'emailb64': email_b64})
        self.assertRedirects(response, expected_url)


class TestActivationView(TestCase):

    def setUp(self):
        """ Cria um usuário inativo para os testes de ativação. """
        self.user = CustomUser.objects.create_user(email='activate@me.com', password='testpassword', is_active=False)

    def test_successful_activation(self):
        """ Testa se um link de ativação válido ativa o usuário. """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, 'Sua conta foi ativada com sucesso!')

    def test_activation_with_invalid_token_redirects_to_resend(self):
        """
        Testa se um link com token inválido redireciona para a página de
        reenvio de ativação.
        """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid-token'
        url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        email_b64 = urlsafe_base64_encode(force_bytes(self.user.email))
        expected_url = reverse('resend_activation', kwargs={'emailb64': email_b64})
        self.assertRedirects(response, expected_url)

    def test_activation_with_invalid_uid_redirects_to_login(self):
        """
        Testa se um link com UID inválido redireciona para a página de login.
        """
        uid = 'invalid-uid'
        token = account_activation_token.make_token(self.user)
        url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))


class TestResendActivationView(TestCase):

    def setUp(self):
        self.inactive_user = CustomUser.objects.create_user(email='resend@test.com', password='password123',
                                                            is_active=False)
        self.active_user = CustomUser.objects.create_user(email='active@test.com', password='password123',
                                                          is_active=True)
        self.email_b64 = urlsafe_base64_encode(force_bytes(self.inactive_user.email))
        self.url = reverse('resend_activation', kwargs={'emailb64': self.email_b64})

    def test_resend_page_loads_correctly(self):
        """ Testa o carregamento da página de reenvio (GET). """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration\\resend_activation.html')
        self.assertContains(response, self.inactive_user.email)

    def test_resend_email_successfully(self):
        """ Testa se o POST reenvia o e-mail com sucesso. """
        response = self.client.post(self.url, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Ative sua conta Growplant.')
        self.assertRedirects(response, self.url)
        self.assertContains(response, 'Um novo e-mail de ativação foi enviado com sucesso.')

    def test_resend_for_active_user_redirects_to_login(self):
        """ Testa se a tentativa de reenvio para um usuário já ativo redireciona para o login. """
        active_email_b64 = urlsafe_base64_encode(force_bytes(self.active_user.email))
        active_url = reverse('resend_activation', kwargs={'emailb64': active_email_b64})
        response = self.client.get(active_url)
        self.assertRedirects(response, reverse('login'))


class TestLoginLogoutViews(TestCase):

    def setUp(self):
        """ Cria dois usuários: um ativo e um inativo. """
        self.active_user_pass = 'testpassword'
        self.active_user = CustomUser.objects.create_user(
            email='active@user.com', password=self.active_user_pass, is_active=True)
        self.inactive_user_pass = 'inactivepass'
        self.inactive_user = CustomUser.objects.create_user(
            email='inactive@user.com', password=self.inactive_user_pass, is_active=False)

    def test_login_page_loads_correctly(self):
        """ Testa se a página de login carrega corretamente (GET). """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration\\login.html')

    def test_successful_login(self):
        """ Testa o login bem-sucedido de um usuário ativo. """
        response = self.client.post(reverse('login'), {
            'email': self.active_user.email,
            'password': self.active_user_pass,
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_with_inactive_user_fails(self):
        """ Testa que um usuário inativo não consegue logar. """
        response = self.client.post(reverse('login'), {
            'email': self.inactive_user.email,
            'password': self.inactive_user_pass,
        }, follow=True)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, 'Sua conta ainda não foi ativada.')

    def test_login_with_wrong_password_fails(self):
        """ Testa que o login com senha errada falha. """
        response = self.client.post(reverse('login'), {
            'email': self.active_user.email,
            'password': 'wrongpassword',
        }, follow=True)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, 'E-mail ou senha inválidos.')

    def successful_logout(self):
        """ Testa se o logout funciona corretamente. """
        self.client.login(email=self.active_user.email, password=self.active_user_pass)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)


class TestPasswordResetViews(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='reset@test.com', password='oldpassword123', is_active=True)

    def test_password_reset_request_sends_email_for_existing_user(self):
        """ Testa se o pedido de redefinição envia e-mail para um usuário válido. """
        response = self.client.post(reverse('password_reset'), {'email': self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_request_does_not_send_email_for_nonexistent_user(self):
        """ Testa que nenhum e-mail é enviado se o e-mail não existir (segurança). """
        response = self.client.post(reverse('password_reset'), {'email': 'nonexistent@email.com'})
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_confirm_and_complete(self):
        """ Testa o fluxo de confirmação e conclusão da redefinição de senha. """
        # Etapa 1: Solicitar o reset e garantir que o e-mail foi enviado
        response = self.client.post(reverse('password_reset'), {'email': self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Etapa 2: Extrair o uid e o token REAIS do corpo do e-mail
        match = re.search(r'reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/', email_body)
        self.assertIsNotNone(match, "Não foi possível encontrar a URL de reset no corpo do e-mail.")

        uidb64 = match.group('uidb64')
        token = match.group('token')

        # Construir a URL com os dados extraídos
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        # Etapa 3: Acessar a página de confirmação (GET)
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200,
                         "A página de confirmação de reset não carregou corretamente.")
        self.assertTemplateUsed(response_get, 'password_reset_confirm.html')
        self.assertTrue(response_get.context['validlink'])

        # Etapa 4: Enviar a nova senha (POST)
        new_password = 'newStrongPassword123'
        response_post = self.client.post(url, {
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response_post, reverse('password_reset_complete'))

        # Etapa 5: Verificar se a senha realmente mudou
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password('oldpassword123'))