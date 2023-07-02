from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrateForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 help_text='Необязательное поле.',
                                 label=_('Имя'))
    last_name = forms.CharField(max_length=30, required=False,
                                help_text='Необязательное поле.',
                                label=_('Фамилия'))
    email = forms.EmailField(max_length=254,
                             help_text='Введите актуальный'
                                       ' адрес электронной почты.'
                                       ' Можно использовать для авторизации.',
                             label=_('Электронная почта'))

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
