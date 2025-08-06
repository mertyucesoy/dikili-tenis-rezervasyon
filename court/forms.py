# court/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'phone', 'password1', 'password2']
        labels = {
            'email': 'E-posta',
            'full_name': 'Ad Soyad',
            'age': 'Yaş',
            'phone': 'Telefon',
            'password1': 'Şifre',
            'password2': 'Şifre (Tekrar)',
        }
        error_messages = {
            'email': {
                'required': 'E-posta adresi gereklidir.',
                'invalid': 'Geçerli bir e-posta adresi giriniz.',
                'unique': 'Bu e-posta ile kayıtlı bir kullanıcı zaten var.',
            },
            'password2': {
                'password_mismatch': 'Şifreler eşleşmiyor.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            "Şifreniz en az 8 karakter olmalı ve yalnızca sayılardan oluşmamalıdır."
        )
        self.fields['password2'].help_text = "Aynı şifreyi tekrar giriniz."
