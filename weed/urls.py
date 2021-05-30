from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('acidlord/', include('acidlord.urls')),
    path('admin/', admin.site.urls),
]