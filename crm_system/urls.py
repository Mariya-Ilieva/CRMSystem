from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lead/', include('crm_system.leads.urls')),
    path('agent/', include('crm_system.agents.urls')),
    path('/', include('crm_system.main.urls')),
]
