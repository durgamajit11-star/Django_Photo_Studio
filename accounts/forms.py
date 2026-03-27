from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# ================= BASE FORM MIXIN =================
class StyledUserCreationForm(UserCreationForm):
    """
    Reusable styling logic for all register forms
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

        # Remove default Django help text
        if 'username' in self.fields:
            self.fields['username'].help_text = None
        if 'password1' in self.fields:
            self.fields['password1'].help_text = None
        if 'password2' in self.fields:
            self.fields['password2'].help_text = None


# ================= USER REGISTER FORM =================
class UserRegisterForm(StyledUserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'USER'
        if commit:
            user.save()
        return user


# ================= STUDIO REGISTER FORM =================
class StudioRegisterForm(StyledUserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'phone',
            'studio_name',
            'owner_name',
            'address',
            'description',
            'license',
            'portfolio',
            'password1',
            'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STUDIO'
        if commit:
            user.save()
        return user


# ================= UPDATE PROFILE FORM =================
class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

from django.contrib.auth.forms import AuthenticationForm


# ================= LOGIN FORM =================
class StyledAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': ' ',   # 🔥 required for floating label
            'required': True,
            'autocomplete': 'username'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': ' ',   # 🔥 required
            'required': True,
            'autocomplete': 'current-password'
        })