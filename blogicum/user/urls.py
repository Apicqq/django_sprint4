from django.conf import settings
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

from user.forms import RegistrateForm

app_name = 'user'

urlpatterns = [
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=RegistrateForm,
        success_url=reverse_lazy('blog:index')),
        name='registration'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
