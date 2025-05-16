from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='travel_input:home'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('travel/', include('travel_input.urls')),
    path('map/', include('map.urls')),
    path('blog/', include('blog.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 