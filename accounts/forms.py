from django import forms
from django.contrib.auth.models import User

from .models import PhoneNumber
from .phone import normalize_phone


class PhoneForm(forms.Form):
    phone = forms.CharField(
        label="Mobile number", max_length=20,
        widget=forms.TextInput(attrs={
            'type': 'tel', 'inputmode': 'tel', 'autocomplete': 'tel', 'autofocus': True,
            'placeholder': '98765 43210',
        }),
    )

    def clean_phone(self):
        number = normalize_phone(self.cleaned_data['phone'])
        if not number:
            raise forms.ValidationError("Enter a valid mobile number (10 digits for India, or +countrycode for others).")
        return number


class SignUpPhoneForm(PhoneForm):
    name = forms.CharField(
        label="Your name", max_length=60,
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'e.g. Riya Sharma'}),
    )

    def clean_phone(self):
        number = super().clean_phone()
        if PhoneNumber.objects.filter(number=number).exists():
            raise forms.ValidationError("This number is already registered. Please log in instead.")
        return number


class LoginPhoneForm(PhoneForm):
    def clean_phone(self):
        number = super().clean_phone()
        if not PhoneNumber.objects.filter(number=number).exists():
            raise forms.ValidationError("No account found for this number. Please sign up first.")
        return number


class OTPForm(forms.Form):
    code = forms.RegexField(
        regex=r'^\d{4,8}$', label="Enter OTP", error_messages={'invalid': "Enter the numeric OTP sent to your phone."},
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric', 'autocomplete': 'one-time-code', 'autofocus': True,
            'maxlength': 8, 'placeholder': '••••••', 'class': 'otp-input',
        }),
    )
