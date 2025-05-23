"""
URL configuration for poketrade2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

__all__ = ["urlpatterns"]
__author__ = "Advaith Menon et al."

from django.contrib import admin
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    # URL for the Accounts app
    path("accounts/", include("accounts.urls")),
    path('admin/', admin.site.urls),
    # Trading gets root priority
    path("", include("trading.urls")),
]


# configure media uploads
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

