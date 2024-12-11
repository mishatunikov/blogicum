from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from blog.models import Comment, Post

User = get_user_model()


class ProfileBaseForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if (User.objects
                .exclude(username=username)
                .filter(email=email)):
            raise forms.ValidationError(
                'Данная электронная почта уже используется.'
            )
        return email


class RegistrationForm(ProfileBaseForm, UserCreationForm):
    pass


class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'is_published',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': '30', 'rows': '8'})
        }
