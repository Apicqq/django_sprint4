from django.conf import settings
from django.urls import include, path

from user.views import SignUpView

app_name = 'user'

urlpatterns = [
    path('auth/registration/', SignUpView.as_view(), name='registration'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
