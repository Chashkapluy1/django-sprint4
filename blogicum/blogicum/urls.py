from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users.views import logout_user

urlpatterns = [
    # Включение URL-адресов приложения blog
    path('', include('blog.urls')),

    # URL-адрес для регистрации пользователя
    path('auth/registration/', include('users.urls')),

    # Включение стандартных URL-адресов Django для аутентификации
    path('auth/', include('django.contrib.auth.urls')),

    # URL-адрес для панели администратора
    path('admin/', admin.site.urls),

    # URL-адрес для выхода пользователя
    path('auth/logout/', logout_user, name='logout'),

    # Включение URL-адресов для статичных страниц
    path('pages/', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработчик ошибок 404
handler404 = 'core.views.page_not_found'

# Обработчик ошибок 500
handler500 = 'core.views.server_error'
