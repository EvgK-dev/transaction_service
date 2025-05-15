import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from .forms import LoginForm, CustomRegisterForm, TransactionForm
from .models import UserProfile

logger = logging.getLogger(__name__)

CATEGORIES = [
    ('Food', 'Еда'),
    ('Transport', 'Транспорт'),
    ('Entertainment', 'Развлечения'),
    ('Utilities', 'Коммунальные услуги'),
    ('Other', 'Другое'),
]

def user_login(request):
    if request.user.is_authenticated:
        logger.info(f"Authenticated user {request.user.username} redirected from login to purchases")
        return redirect(reverse('purchases'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                logger.info(f"User {cd['username']} logged in successfully")
                return redirect(reverse('purchases'))
            else:
                logger.warning(f"Failed login attempt for username {cd['username']}")
                messages.error(request, 'Неверные имя пользователя или пароль.')
        else:
            logger.warning(f"Invalid login form submitted: {form.errors}")
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = LoginForm()

    return render(request, 'mainapp/login.html', {'form': form})

def create_user_profile(user, daily_limit, weekly_limit, balance):
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.daily_limit = daily_limit
    user_profile.weekly_limit = weekly_limit
    user_profile.balance = balance
    user_profile.save()
    return user_profile

def register(request):
    if request.user.is_authenticated:
        logger.info(f"Authenticated user {request.user.username} redirected from register to purchases")
        return redirect(reverse('purchases'))

    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=cd['username'],
                    password=cd['password1']
                )
                create_user_profile(
                    user=user,
                    daily_limit=cd['daily_limit'],
                    weekly_limit=cd['weekly_limit'],
                    balance=cd['balance']
                )
                login(request, user)
                logger.info(f"User {cd['username']} registered and logged in successfully")
                messages.success(request, 'Вы успешно зарегистрированы и вошли в систему.')
                return redirect(reverse('purchases'))
            except IntegrityError:
                logger.warning(f"Registration failed: Username {cd['username']} already exists")
                messages.error(request, 'Имя пользователя уже занято.')
            except Exception as e:
                logger.error(f"Registration error for {cd['username']}: {str(e)}")
                messages.error(request, 'Произошла ошибка при регистрации.')
        else:
            logger.warning(f"Invalid registration form submitted: {form.errors}")
            for error in form.non_field_errors():
                messages.error(request, error)
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = CustomRegisterForm()

    return render(request, 'mainapp/register.html', {'form': form})

@login_required
def purchases_view(request):
    logger.debug(f"User {request.user.username} accessed purchases view")
    return render(request, 'mainapp/purchases.html', {'categories': CATEGORIES})

def user_logout(request):
    username = request.user.username if request.user.is_authenticated else 'anonymous'
    logout(request)
    logger.info(f"User {username} logged out successfully")
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect(reverse('login'))