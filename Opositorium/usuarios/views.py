from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegistroForm
from django.shortcuts import render, redirect
from django.urls import path

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/examinador/")
            else:
                form.add_error(None, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    return render(request, "usuarios/login.html", {"form": form})

def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("/examinador/")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("/")