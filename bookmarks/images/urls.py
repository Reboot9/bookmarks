from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('create/', views.ImageCreateView.as_view(), name='create'),
    path('detail/<int:id>/<slug:slug>/', views.ImageDetailView.as_view(), name='detail')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)