from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.utils.translation import gettext as _


def register_view(request):
    """Benutzer-Registrierungsseite"""
    if request.user.is_authenticated:
        return redirect('cv_manager:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Ihr Konto wurde erstellt! Sie können sich jetzt anmelden.'))
            login(request, user)
            return redirect('cv_manager:dashboard')
    else:
        form = UserCreationForm()

    # Bootstrap-Klasse hinzufügen
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.update({'class': 'form-control'})

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Benutzer-Anmeldeseite"""
    if request.user.is_authenticated:
        return redirect('cv_manager:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('Willkommen, %(username)s!') % {'username': username})
                next_url = request.GET.get('next', 'cv_manager:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, _('Ungültiger Benutzername oder Passwort.'))
        else:
            messages.error(request, _('Ungültiger Benutzername oder Passwort.'))
    else:
        form = AuthenticationForm()
    
    # Bootstrap-Klasse hinzufügen
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Benutzer-Abmeldung"""
    logout(request)
    messages.info(request, _('Sie wurden erfolgreich abgemeldet.'))
    return redirect('users:login')
