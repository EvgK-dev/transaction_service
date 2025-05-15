from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Transaction


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    captcha = CaptchaField()


class CustomRegisterForm(UserCreationForm):
    daily_limit = forms.DecimalField(label="Лимит на день", min_value=0, required=True)
    weekly_limit = forms.DecimalField(label="Лимит на неделю", min_value=0, required=True)
    balance = forms.DecimalField(label="Текущий баланс", min_value=0, required=True)
    captcha = CaptchaField(label="Введите капчу")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'daily_limit', 'weekly_limit', 'balance', 'captcha']


class TransactionForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'required': True}),
        label="Дата покупки"
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'currency', 'category', 'timestamp']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'required': True, 'value': '200'}),
            'currency': forms.TextInput(attrs={'value': 'RUB', 'readonly': True}),
            'category': forms.HiddenInput(),  
        }