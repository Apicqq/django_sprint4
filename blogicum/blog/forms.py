from django import forms
from django.contrib.auth import get_user_model

from blog.models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(format='%d/%m/%Y %H:%M', attrs={
                'type': 'datetime-local',
            })}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('author', 'post',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_active')
        widgets = {
            'password': forms.PasswordInput()

        }
