from rest_framework import permissions
from API.models import *


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class OnlyPMorQALeadCanEdit(permissions.BasePermission):
    """
    Custom permission to only allow PM and QA Leads to some object.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, (ProjectTeam, Issue)):
            project = obj.project
        elif isinstance(obj, (Worklog, IssueAttachment, IssueLink, Comment)):
            project = obj.issue.project
        else:
            return False
        leads = ProjectTeam.objects.filter(project=project, team_role__in=['PM', 'QALEAD'])
        team = ProjectTeam.objects.filter(project=project)
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS and request.user in [member.user for member in team]:
            return True
        # Write permissions are only allowed to the qa lead or PM
        if request.user in [member.user for member in leads]:
            return True
        # Superuser has full access to all endpoints
        return request.user and request.user.is_staff


class IsProjectTeamOnly(permissions.BasePermission):
    """
    Custom permission to only allow PM and QA Leads to some object.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, (ProjectTeam, Issue)):
            project = obj.project
        elif isinstance(obj, (Worklog, IssueAttachment, IssueLink, Comment)):
            project = obj.issue.project
        else:
            return False
        team = ProjectTeam.objects.filter(project=project)
        # Write permissions are only allowed to the project team
        if request.user in [member.user for member in team]:
            return True
        # Superuser has full access to all endpoints
        return request.user and request.user.is_staf