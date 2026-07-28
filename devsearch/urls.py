from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('project_app.urls')),
    path('users/', include('users.urls')),
]