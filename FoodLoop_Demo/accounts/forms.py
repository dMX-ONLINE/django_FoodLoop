from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Enter your username",
            "autocomplete": "username",
        }),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        }),
    )


class SignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
    )

    email = forms.EmailField(
        required=True,
        label="Email Address",
    )

    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number",
    )

    terms = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must agree to the terms and conditions."
        },
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose another."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()

        if phone and not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise forms.ValidationError(
                "Enter a valid phone number."
            )

        return phone

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"].strip().lower()
        user.role = "customer"

        if hasattr(user, "phone_number"):
            user.phone_number = self.cleaned_data.get("phone_number", "").strip()

        if commit:
            user.save()

        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone_number',
            'pickup_address',
            'bio',
            'avatar',
        ]

        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
            'pickup_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your pickup address',
                'rows': 3,
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us a little about yourself',
                'rows': 4,
            }),
        }
