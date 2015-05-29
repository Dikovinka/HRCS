from rest_framework import serializers
from API.models import *
import re
from datetime import datetime

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(required=True, max_length=100)
    project_description = serializers.CharField(required=False, allow_blank=True, max_length=100)
    created = serializers.DateTimeField(read_only=True)
    # project_manager = serializers.PrimaryKeyRelatedField(queryset=APIUser.objects.filter(id__in=[unit.user_id for unit in UserPermission.objects.filter(permission_id=1)]))

    class Meta:
        model = Project
        fields = ('url', 'abbr', 'project_manager',
                  'title', 'project_description', 'team_only', 'created',)
        read_only_fields = ('created', 'abbr')

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
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        fields = ('url', 'id', 'permission_name', 'permission_type', 'permission_description',)

    def create(self, validated_data):
        """
        Create and return a new `Permission` instance, given the validated data.
        """
        return Permission.objects.create(**validated_data)


class UserPermissionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserPermission
        fields = ('url', 'user', 'permission',)

    def create(self, validated_data):
        """
        Create and return a new `User Permission` instance, given the validated data.
        """
        # user=User.objects.get(username=validated_data['user']),
        return UserPermission.objects.create(**validated_data)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    retype_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True, help_text="Password should be at least 6 characters long")
    class Meta:
        model = APIUser
        fields = ('url', 'first_name', 'last_name', 'username', 'email', 'date_joined', 'last_login', 'password', 'retype_password')
        read_only_fields = ('date_joined', 'last_login',)

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


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    highlight = serializers.HyperlinkedIdentityField(view_name='issue-highlight', format='html')

    class Meta:
        model = Issue
        fields = (
            'url',
            'highlight',
            'issue_key',
            'project_id',
            'title',
            'issue_description',
            'status',
            'type',
            'created',
            'updated',
            'created_by',
            'assigned_to',
            'highlighted',
        )
        read_only_fields = ('status', 'created', 'issue_key', 'updated', 'created_by', 'highlighted', )

    def create(self, validated_data):
        """
        Create and return a new `Issue` instance, given the validated data.
        """
        validated_data['issue_key'] = "{}-{}".format(validated_data['project_id'].abbr, Issue.objects.count() + 1)
        validated_data['status'] = 'OPENED'
        return Issue.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.issue_description = validated_data.get('issue_description', instance.issue_description)
        instance.status = validated_data.get('status', instance.status)
        instance.updated = datetime.now()
        instance.save()
        return instance