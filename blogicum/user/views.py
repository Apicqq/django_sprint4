from django.views.generic import CreateView
from django.urls import reverse_lazy
from user.forms import RegistrateForm


class SignUpView(CreateView):
    form_class = RegistrateForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'
