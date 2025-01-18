"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django_project.app import app

app.add_router("v1", "apps.core.views.router")
app.add_router("v1", "apps.chat.endpoints.router")  # chat 앱의 router 추가
app.add_router("v1", "apps.answer.views.router")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", app.urls),
    path("", include('apps.chat.urls')),  # chat 앱의 템플릿 뷰 URL 추가
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)