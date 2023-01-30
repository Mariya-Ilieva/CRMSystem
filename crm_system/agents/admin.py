from django.contrib import admin

from crm_system.agents.models import User, Agent, Profile

admin.site.register(User)
admin.site.register(Agent)
admin.site.register(Profile)
