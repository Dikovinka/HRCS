from django.contrib import admin
from .models import Project, ProjectTeam

# Register your models here.
class ProjectTeamLine(admin.StackedInline):
    model = ProjectTeam
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectTeamLine]
    list_filter = ['title']
admin.site.register(Project, ProjectAdmin)
