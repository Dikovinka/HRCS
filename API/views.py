from django.views.decorators.csrf import csrf_exempt
from API.models import *
from API.serializers import *
from rest_framework import permissions
from API.permissions import IsOwnerOrReadOnly, OnlyPMorQALeadCanEdit, IsProjectTeamOnly
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from django.contrib.auth.models import User
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = APIUser.objects.all()
    serializer_class = UserSerializer
    def perform_create(self, serializer):
            serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if(request.query_params):
            serializer = self.get_serializer(instance, data=request.query_params, partial=partial)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (OnlyPMorQALeadCanEdit,)

    def perform_create(self, serializer):
            serializer.save()


class ProjectTeamViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ProjectTeam.objects.all()
    serializer_class = ProjectTeamSerializer
    permission_classes = (OnlyPMorQALeadCanEdit,)

    def perform_create(self, serializer):
            serializer.save()

    def create(self, request, *args, **kwargs):
        if(request.query_params):
            serializer = self.get_serializer(data=request.query_params)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class IssueViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsProjectTeamOnly)

    def create(self, request, *args, **kwargs):
        if(request.query_params):
            serializer = self.get_serializer(data=request.query_params)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=APIUser.objects.get(id=self.request.user.id))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if(request.query_params):
            serializer = self.get_serializer(instance, data=request.query_params, partial=partial)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsProjectTeamOnly)

    def create(self, request, *args, **kwargs):
        if(request.query_params):
            serializer = self.get_serializer(data=request.query_params)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=APIUser.objects.get(id=self.request.user.id))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if(request.query_params):
            serializer = self.get_serializer(instance, data=request.query_params, partial=partial)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class WorklogViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Worklog.objects.all()
    serializer_class = WorklogSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsProjectTeamOnly)

    def create(self, request, *args, **kwargs):
        if(request.query_params):
            serializer = self.get_serializer(data=request.query_params)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=APIUser.objects.get(id=self.request.user.id))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if(request.query_params):
            print(request.query_params)
            serializer = self.get_serializer(instance, data=request.query_params, partial=partial)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)