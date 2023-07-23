import redis
from actions.utils import create_action
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, View

from .forms import ImageCreateForm
from .models import Image

# connect to Redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class ImageCreateView(LoginRequiredMixin, CreateView):
    model = Image
    form_class = ImageCreateForm
    template_name = 'images/image/create.html'

    def form_valid(self, form):
        cd = form.cleaned_data
        new_image = form.save(commit=False)
        new_image.user = self.request.user
        new_image.save()
        create_action(self.request.user, 'bookmarked image', new_image)
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

        # increment number of views using redis
        image_id = self.object.id
        # r.set(f'image:{image_id}:views', 0)
        # total_views = r.incr(f'image:{image_id}:views')
        # r.delete(f'image:{image_id}:views')
        # # print(r.type(f'image:{image_id}:views'))
        r.sadd(f'image:{image_id}:views', self.request.user.id)
        # returns cardinality(length) of a set that contains unique user views
        total_views = r.scard(f'image:{image_id}:views')
        context['total_views'] = total_views

        return context


class ImageLikeView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)

        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):
        image_id = request.POST.get('id')
        # Determines what user wants to like image or remove like
        action = request.POST.get('action')
        if image_id and action:
            image = get_object_or_404(Image, id=image_id)

            if action == 'like':
                image.like.add(request.user)
                create_action(self.request.user, 'likes', image)
            else:
                image.like.remove(request.user)

            return JsonResponse({'status': 'ok'})

        return JsonResponse({'status': 'error'})


class ImageListView(LoginRequiredMixin, ListView):
    template_name = 'images/image/list.html'
    model = Image
    paginate_by = 8
    context_object_name = 'images'
    images_only = False
    section = 'images'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

    def get(self, request, *args, **kwargs):
        self.kwargs[self.page_kwarg] = request.GET.get(self.page_kwarg, 1)

        paginator = self.get_paginator(self.get_queryset(), self.paginate_by)
        page = self.kwargs[self.page_kwarg]
        images_only = self.request.GET.get('images_only')

        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            if images_only:
                # If it's an AJAX request and page is out of range, return an empty page
                return HttpResponse('')

            # If page is not an integer or out of range, deliver the first page
            page_obj = paginator.page(1)

        return super().get(request, *args, page_obj=page_obj, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.section
        context['images_only'] = self.request.GET.get('images_only') is not None
        return context

    def render_to_response(self, context, **response_kwargs):
        images_only = self.request.GET.get('images_only') is not None
        if images_only:
            self.template_name = 'images/image/image_list.html'
        return super().render_to_response(context, **response_kwargs)
