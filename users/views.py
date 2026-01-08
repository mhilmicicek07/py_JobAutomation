from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


def register_view(request):
    """Kullanıcı kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('cv_manager:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hesabınız oluşturuldu! Şimdi giriş yapabilirsiniz.')
            login(request, user)
            return redirect('cv_manager:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Kullanıcı giriş sayfası"""
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
                messages.success(request, f'Hoş geldiniz, {username}!')
                next_url = request.GET.get('next', 'cv_manager:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    else:
        form = AuthenticationForm()
    
    # Bootstrap class ekle
    for field_name in form.fields:
        form.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Kullanıcı çıkış"""
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('users:login')
