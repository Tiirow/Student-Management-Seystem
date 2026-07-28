from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .forms import RegisterForm


def registerUser(request):

    if request.user.is_authenticated:
        return redirect('projects')
   #✔️ Tani waa muhiim. User login ah mar kale looma oggola /login ama /register.

    form = RegisterForm()

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(request, 'Account created successfully.')

            return redirect('projects')

    context = {
        'form': form
    }

    return render(request, 'users/register.html', context)


def loginUser(request):

    if request.user.is_authenticated:
        return redirect('projects')

    if request.method == 'POST':

        username = request.POST.get('username', '').lower()
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('projects')

        messages.error(
            request,
            'Username OR Password is incorrect.'
        )

    return render(
        request,
        'users/login.html'
    )


def logoutUser(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out.'
    )

    return redirect('login')