from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import user_login, dashboard, register, edit, user_detail, \
    user_list, user_follow
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path("login/", user_login, name='login')
    path('', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('edit/', edit, name='edit'),
    path('users/', user_list, name='user_list'),
    path('users/follow/', user_follow, name='user_follow'),
    path('users/<username>/', user_detail, name='user_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)

