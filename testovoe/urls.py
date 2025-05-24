from django.contrib import admin
from django.urls import path, include

#по идее админ панель не нужна,но пусть будет
#также прописывает что по умолчанию идем в приложение users и берем его адреса

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
]