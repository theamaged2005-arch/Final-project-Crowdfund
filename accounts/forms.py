from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class BootstrapFormMixin:
    """بيضيف كلاس form-control لكل حقل تلقائيًا عشان يبقى شكله حلو مع Bootstrap"""
    def _apply_bootstrap(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()


class RegistrationForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True, help_text="e.g. 01012345678")
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.email = self.cleaned_data['email']
        user.is_active = True
        user.is_activated = False
        if commit:
            user.save()
        return user


class LoginForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

class ProfileEditForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile_picture', 'birthdate', 'facebook_profile', 'country']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class AccountDeleteForm(BootstrapFormMixin, forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Confirm your password")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise ValidationError("Incorrect password.")
        return password
class PasswordResetRequestForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class SetNewPasswordForm(BootstrapFormMixin, forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New password")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('new_password1'), cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return cleaned