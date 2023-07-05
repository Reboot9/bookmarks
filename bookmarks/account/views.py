from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
# from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView, UpdateView

from .forms import LoginForm, UserRegistrationForm, UserEditForm
from .models import Profile


class LoginView(View):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        message = ''

        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return HttpResponse('Authenticated successfully')
        message = 'Login failed!'
        return render(request, self.template_name, context={'form': form, 'message': message})


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {
        'section': 'dashboard',
    })


class UserRegistrationView(UserPassesTestMixin, CreateView):
    model = Profile  # User
    form_class = UserRegistrationForm
    template_name = 'account/register.html'
    success_url = 'account/register_done.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(reverse_lazy('dashboard'))

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        return render(self.request, self.success_url, {'new_user': user})


class UserEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UserEditForm
    template_name = 'account/edit.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.has_changed():
            messages.success(self.request, 'Profile updated successfully.')

        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Error updating your profile')

        return response
