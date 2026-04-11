from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Your account is ready.")
            return redirect('dashboard:home')
        else:
            # Pass back with register tab active
            return render(request, 'users/auth.html', {
                'register_form': form,
                'login_form': LoginForm(request),
                'active_tab': 'register',
            })

    return render(request, 'users/auth.html', {
        'register_form': RegisterForm(),
        'login_form': LoginForm(request),
        'active_tab': 'register',
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            return render(request, 'users/auth.html', {
                'login_form': form,
                'register_form': RegisterForm(),
                'active_tab': 'login',
            })

    return render(request, 'users/auth.html', {
        'login_form': LoginForm(request),
        'register_form': RegisterForm(),
        'active_tab': 'login',
    })


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('users:login')
