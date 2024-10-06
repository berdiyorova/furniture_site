from django.urls import path

from users.views import account_view, register_view, login_view, verify_email

app_name = 'users'

urlpatterns = [
    path('account/', account_view, name='account'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify-email/<uidb64>/<token>', verify_email, name='verify_email'),
]