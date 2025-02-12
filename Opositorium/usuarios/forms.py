from django.contrib.auth.models import User
from django import forms

class RegistroForm(forms.ModelForm):
    username = forms.CharField(label="Usuario", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Elige tu contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirma la contraseña")

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado. Prueba con otro.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
