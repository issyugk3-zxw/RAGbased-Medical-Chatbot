from django.contrib import admin
from django.urls import path, include
from userapi.admin import mongo_admin_site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("mongoadmin/", mongo_admin_site.urls),
    path("userapi/", include("userapi.urls")),
    path("agentapi/", include("agentapi.urls")),
    path("sessionapi/", include("sessionapi.urls"))
]
