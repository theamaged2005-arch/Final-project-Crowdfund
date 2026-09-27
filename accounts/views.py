from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import (
    RegistrationForm, LoginForm, ProfileEditForm, AccountDeleteForm,
    PasswordResetRequestForm, SetNewPasswordForm,
)
from .tokens import make_activation_token, check_activation_token

User = get_user_model()


def _absolute_url(request, path):
    return f"{settings.SITE_PROTOCOL}://{request.get_host()}{path}"


def _send_activation_email(request, user):
    token = make_activation_token(user)
    link = _absolute_url(request, reverse('accounts:activate', args=[token]))
    subject = "Activate your Crowdfund EG account"
    body = (
        f"Hi {user.first_name},\n\n"
        f"Please activate your account by clicking the link below:\n{link}\n\n"
        f"This link expires in {settings.ACTIVATION_LINK_EXPIRY_HOURS} hours.\n\n"
        f"- Crowdfund EG Team"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            _send_activation_email(request, user)
            messages.success(request, "Account created! Check your email (or the terminal) for an activation link.")
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, token):
    uid = check_activation_token(token)
    if uid is None:
        return render(request, 'accounts/activation_invalid.html', status=400)

    user = get_object_or_404(User, pk=uid)
    if user.is_activated:
        messages.info(request, "Your account is already activated.")
    else:
        user.is_activated = True
        user.save(update_fields=['is_activated'])
        messages.success(request, "Your account has been activated. You can now log in.")
    return redirect('accounts:login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, email=email, password=password)
            if user is None:
                messages.error(request, "Invalid email or password.")
            elif not user.is_activated:
                messages.error(request, "Please activate your account first - check your email.")
            else:
                login(request, user)
                return redirect('core:home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:home')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def account_delete(request):
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, "Your account has been permanently deleted.")
            return redirect('core:home')
    else:
        form = AccountDeleteForm(user=request.user)
    return render(request, 'accounts/account_delete_confirm.html', {'form': form})
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                token = make_activation_token(user)
                link = _absolute_url(request, reverse('accounts:password_reset_confirm', args=[token]))
                subject = "Reset your Crowdfund EG password"
                body = (
                    f"Hi {user.first_name},\n\n"
                    f"Click the link below to reset your password:\n{link}\n\n"
                    f"This link expires in {settings.ACTIVATION_LINK_EXPIRY_HOURS} hours.\n\n"
                    f"- Crowdfund EG Team"
                )
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            except User.DoesNotExist:
                pass
            messages.success(request, "If that email is registered, a reset link has been sent.")
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    uid = check_activation_token(token)
    if uid is None:
        return render(request, 'accounts/activation_invalid.html', status=400)
    user = get_object_or_404(User, pk=uid)

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save(update_fields=['password'])
            messages.success(request, "Password updated. You can now log in.")
            return redirect('accounts:login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})