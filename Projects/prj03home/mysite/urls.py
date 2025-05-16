from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),                         # 관리자 페이지
    path('', accounts_views.home, name='home'),              # 기본 홈화면 (accounts.views.home)
    path('accounts/', include('accounts.urls')),             # 회원 기능 라우팅
    path('travel/', include('travel_input.urls')),           # 여행 기능 전체 (⭐ 반드시 존재해야 함)
    path('map/', include('map.urls')),                       # 지도 기능 라우팅
    path('blog/', include('blog.urls')),                     # 블로그 기능 라우팅
]

# 개발 환경에서 MEDIA 파일 접근 허용
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
