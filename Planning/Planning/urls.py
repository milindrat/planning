"""
URL configuration for Planning_Automation project.

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
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',include('consensus_planning.urls')),
    path('login/',include('consensus_planning.urls')),
    path('logout_user/',include('consensus_planning.urls')),
    path('file_upload/',include('consensus_planning.urls')),
    path('change_user/',include('consensus_planning.urls')),
    path('user/',include('consensus_planning.urls')),
    path('permission/',include('consensus_planning.urls')),
    path('item_list/',include('consensus_planning.urls')),
   

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)