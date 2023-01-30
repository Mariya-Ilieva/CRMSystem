from django.contrib import admin

from crm_system.leads.models import Lead, Category, FollowUp


class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age', 'email']
    list_display_links = ['first_name']
    list_editable = ['last_name']
    list_filter = ['category']
    search_fields = ['first_name', 'last_name', 'email']


admin.site.register(Category)
admin.site.register(Lead, LeadAdmin)
admin.site.register(FollowUp)
