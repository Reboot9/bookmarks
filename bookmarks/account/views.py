from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
# from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from django.contrib.auth.views import LoginView

from .forms import LoginForm, UserRegistrationForm, UserEditForm
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action


# class LoginView(View):
#     template_name = 'account/login.html'
#     form_class = LoginForm
#
#     def get(self, request):
#         form = self.form_class()
#
#         return render(request, self.template_name, context={
#             'form': form,
#         })
#
#     def post(self, request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             user = authenticate(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password'],
#             )
#             if user is not None:
#                 login(request, user)
#                 return HttpResponse('Authenticated successfully')
#         return render(request, self.template_name, context={'form': form})


@login_required
def dashboard(request):
    # by default, show all actions
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # if user is following other users, show only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user')[:10].prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html', {
        'section': 'dashboard',
        'actions': actions
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
        create_action(user, 'has created an account')
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


class UserLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class UserListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'account/list.html'
    context_object_name = 'users'
    section = 'people'

    def get_queryset(self):
        # excluding sender from the profiles list
        return Profile.objects.filter(is_active=True).exclude(id=self.request.user.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section

        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'account/detail.html'
    section = 'people'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(Profile, username=username, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section

        return context


class UserFollowView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)

        return HttpResponseNotAllowed(['POST'])

    def post(self, request):
        user_id = request.POST.get('id')
        action = request.POST.get('action')
        if user_id and action:
            user = get_object_or_404(Profile, id=user_id)

            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'})
