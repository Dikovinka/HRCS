from django.contrib import admin
from .models import Project, Worklog

# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_filter = ['title']
admin.site.register(Project, ProjectAdmin)
admin.site.register(Worklog)
