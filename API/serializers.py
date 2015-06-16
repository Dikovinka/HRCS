from rest_framework import serializers
from API.models import *
import re
from django.utils import timezone


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment

        fields = (
            'id',
            'url',
            'issue',
            'author',
            'comment',
            'created',
            'updated',
        )
        read_only_fields = ('created', 'updated', 'author',)

    def create(self, validated_data):
        """
        Create and return a new `Comment` instance, given the validated data.
        """
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Comment` instance, given the validated data.
        """
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.updated = timezone.now()
        instance.save()
        return instance


class WorklogSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Worklog

        fields = (
            'id',
            'url',
            'user',
            'issue',
            'created',
            'updated',
            'work_date',
            'work_hours',
            'work_minutes',
        )
        read_only_fields = ('created', 'updated', 'user',)

    def create(self, validated_data):
        """
        Create and return a new `WorkLog` instance, given the validated data.
        """
        return Worklog.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLog` instance, given the validated data.
        """
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.updated = timezone.now()
        instance.save()
        return instance


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    issue_comments = CommentSerializer(many=True, read_only=True)
    issue_worklogs = WorklogSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = (
            'id',
            'url',
            'issue_key',
            'project',
            'title',
            'issue_description',
            'status',
            'type',
            'priority',
            'created',
            'updated',
            'created_by',
            'assigned_to',
            'issue_comments',
            'issue_worklogs',
        )
        read_only_fields = ('created', 'issue_key', 'updated', 'created_by',)

    def create(self, validated_data):
        """
        Create and return a new `Issue` instance, given the validated data.
        """
        validated_data['issue_key'] = "{}-{}".format(validated_data['project'].abbr, Issue.objects.filter(project=validated_data['project']).count() + 1)
        validated_data['status'] = 'OPENED'
        return Issue.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Issue` instance, given the validated data.
        """
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.updated = timezone.now()
        instance.save()
        return instance


class ProjectTeamSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectTeam
        fields = ('url', 'user', 'project', 'team_role',)

    def create(self, validated_data):
        """
        Create and return a new `ProjectTeam` instance, given the validated data.
        """
        return ProjectTeam.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `ProjectTeam` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(required=True, max_length=100)
    project_description = serializers.CharField(required=False, allow_blank=True, max_length=100)
    created = serializers.DateTimeField(read_only=True)
    project_team = ProjectTeamSerializer(many=True, read_only=True)
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'url', 'abbr', 'project_manager',
                  'title', 'project_description', 'created', 'project_team', 'issues', )
        read_only_fields = ('id', 'url', 'created', 'abbr')

    def create(self, validated_data):
        """
            Create and return a new `Project` instance, given the validated data.
        """
        validated_data['abbr'] = (re.sub(r'[AEIOU]', '', validated_data['title'], flags=re.IGNORECASE)).replace(' ', '').upper()
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Project` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.abbr = (re.sub(r'[AEIOU]', '', instance.title, flags=re.IGNORECASE)).replace(' ', '').upper()
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    retype_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True, help_text="Password should be at least 6 characters long")
    user_projects = ProjectTeamSerializer(many=True, read_only=True)
    my_worklogs = WorklogSerializer(many=True, read_only=True)

    class Meta:
        model = APIUser
        fields = ('id', 'url', 'first_name', 'last_name', 'username', 'email', 'date_joined', 'last_login', 'password', 'retype_password', 'user_projects', 'my_worklogs',)
        read_only_fields = ('date_joined', 'last_login', 'user_projects', )

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        if (len(validated_data['password']) < 6 ):
            raise serializers.ValidationError({'password' : ['Password should be at least 6 characters long']})
        if (validated_data['password'] != validated_data['retype_password']):
            raise serializers.ValidationError({'retype_password': ['Password and retype password field values should match.']})
        else:
            del validated_data['retype_password']
            return APIUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


