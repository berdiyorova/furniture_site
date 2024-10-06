import base64

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives

from config.settings import EMAIL_HOST_USER
from users.forms import RegistrationForm, LoginForm
from users.models import UserModel
from users.token import email_verification_token

def account_view(request):
    return render(request, 'registration/user-account.html')


def verify_email(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = UserModel.objects.get(pk=uid)
    if user is not None and email_verification_token.check_token(user=user, token=token):
        user.is_active = True
        user.save()
        return redirect(reverse_lazy('users:login'))
    else:
        return render(request, 'registration/email_not_verified.html')


def send_email_verification(request, user):
    token = email_verification_token.make_token(user)
    user_id = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    verification_url = reverse('users:verify_email', kwargs={'uidb64': user_id, 'token': token})
    full_url = f"http://{current_site.domain}{verification_url}"

    text_content = render_to_string(
        'registration/verify_email.html',
        {'user': user, 'full_url': full_url}
    )

    message = EmailMultiAlternatives(
        subject='Verification Email',
        body=text_content,
        to=[user.email],
        from_email=EMAIL_HOST_USER
    )
    message.attach_alternative(text_content, 'text/html')
    message.send()


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(raw_password=form.cleaned_data['password'])
            user.is_active = False
            user.save()
            send_email_verification(request, user)
            return HttpResponse("Email is sent to your email address.")
        else:
            errors = form.errors
            return render(request, 'registration/user-register.html', {'errors': errors})
    else:
        form = RegistrationForm()
        return render(request, 'registration/user-register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                login(request, user)  # Log the user in (get token)
                return redirect('common:home')  # Adjust this URL as needed
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/user-login.html', {'form': form})
