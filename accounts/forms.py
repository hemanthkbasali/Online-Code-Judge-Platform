"""Forms for registration and login."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from accounts.models import User


class BootstrapFormMixin:
    """Apply Bootstrap classes in one place so templates stay clean."""

    def _apply_bootstrap(self):
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} form-control".strip()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=120, required=False)
    institution = forms.CharField(max_length=180, required=False)

    class Meta:
        model = User
        fields = ("username", "display_name", "email", "institution", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
        self.fields["username"].widget.attrs.update({"placeholder": "Choose a username"})
        self.fields["display_name"].widget.attrs.update({"placeholder": "Your display name"})
        self.fields["email"].widget.attrs.update({"placeholder": "you@example.com"})
        self.fields["institution"].widget.attrs.update({"placeholder": "College or organization"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Create password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self._apply_bootstrap()
        self.fields["username"].widget.attrs.update({"placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})
