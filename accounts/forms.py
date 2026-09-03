from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BuyerRegistrationForm(UserCreationForm):
    """
    Buyer self-registration form. Built on top of Django's built-in
    UserCreationForm (which already handles username uniqueness and
    password confirmation/strength checks) - we just add a required email.
    """
    email = forms.EmailField(required=True, help_text="Used for auction notifications.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
