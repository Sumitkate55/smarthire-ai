from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100, required=True, label="Full Name",
        widget=forms.TextInput(attrs={'class': 'sh-input', 'placeholder': 'Sumit Kate'})
    )
    email = forms.EmailField(
        required=True, label="Email",
        widget=forms.EmailInput(attrs={'class': 'sh-input', 'placeholder': 'you@email.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'sh-input', 'placeholder': 'sumit_dev'})
        self.fields['password1'].widget.attrs.update({'class': 'sh-input', 'placeholder': 'Min 8 characters'})
        self.fields['password2'].widget.attrs.update({'class': 'sh-input', 'placeholder': 'Repeat password'})
        # Remove help texts for cleaner UI
        for field in self.fields.values():
            field.help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        full = self.cleaned_data.get('full_name', '').strip().split(' ', 1)
        user.first_name = full[0]
        user.last_name = full[1] if len(full) > 1 else ''
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'sh-input', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'sh-input', 'placeholder': '••••••••'})
        for field in self.fields.values():
            field.help_text = ''
