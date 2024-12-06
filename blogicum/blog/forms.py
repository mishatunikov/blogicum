from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm


User = get_user_model()


class ProfileBaseForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        print(username)
        if (User.objects
                .exclude(username=username)
                .filter(email=email)):
            raise forms.ValidationError(
                'Данная электронная почта уже используется.'
            )
        return email


class RegistrationForm(ProfileBaseForm, UserCreationForm):
    pass
