from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .models import Image
from .forms import ImageCreateForm


class ImageCreateView(LoginRequiredMixin, CreateView):
    model = Image
    form_class = ImageCreateForm
    template_name = 'images/image/create.html'

    def form_valid(self, form):
        cd = form.cleaned_data
        new_image = form.save(commit=False)
        new_image.user = self.request.user
        new_image.save()
        messages.success(self.request, 'Image added successfully')
        return redirect(new_image.get_absolute_url())

    def get(self, request, *args, **kwargs):
        form = self.form_class(data=request.GET)
        return self.render_to_response({'section': 'images', 'form': form})


class ImageDetailView(DetailView):
    model = Image
    template_name = 'images/image/detail.html'
    context_object_name = 'image'

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        slug = self.kwargs.get('slug')

        return get_object_or_404(Image, id=id, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'images'

        return context