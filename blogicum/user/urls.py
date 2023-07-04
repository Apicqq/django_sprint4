from django.urls import path

from user.views import SignUpView

app_name = 'user'

urlpatterns = [
    path('auth/registration/', SignUpView.as_view(), name='registration'),
]
