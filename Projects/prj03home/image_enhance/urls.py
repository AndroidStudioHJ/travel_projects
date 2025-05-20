from django.urls import path
from .views import image_enhance_view, process_image, get_available_nafnet_options

urlpatterns = [
    path('', image_enhance_view, name='image_enhance'),
    path('process/', process_image, name='process_image'),
    path('get-options/', get_available_nafnet_options, name='get_available_nafnet_options'),
]