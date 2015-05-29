# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(blank=True)),
                ('highlighted', models.TextField()),
            ],
            options={
                'ordering': ('issue_id', 'created'),
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('issue_key', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('issue_description', models.CharField(blank=True, max_length=100, default='')),
                ('status', models.CharField(choices=[('OPENED', 'Opened'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')], max_length=100, default=('OPENED', 'Opened'))),
                ('type', models.CharField(choices=[('TASK', 'Task'), ('BUG', 'Bug'), ('SUB_TASK', 'Sub Task')], max_length=100, default=('TASK', 'Task'))),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(blank=True)),
                ('highlighted', models.TextField()),
            ],
            options={
                'ordering': ('project_id', 'created'),
            },
        ),
        migrations.CreateModel(
            name='IssueAttachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('attachment_name', models.CharField(max_length=100)),
                ('datetime_added', models.DateTimeField(auto_now_add=True)),
                ('attachment', models.FileField(upload_to='attachments')),
                ('issue_id', models.ForeignKey(to='API.Issue', related_name='attachments')),
            ],
            options={
                'ordering': ('attachment_name', 'datetime_added'),
            },
        ),
        migrations.CreateModel(
            name='IssueLink',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('link_type', models.CharField(choices=[('PARENT', 'Parent'), ('CHILD', 'Child'), ('RELATED_TO', 'Related to'), ('DUPLICATES', 'Duplicates'), ('BLOCKED_BY', 'Blocked by')], max_length=100)),
                ('issue_id', models.ForeignKey(to='API.Issue', related_name='link_issue_id')),
                ('linked_issue_id', models.ForeignKey(to='API.Issue', related_name='linked_issue_id')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('permission_name', models.CharField(max_length=100, unique=True)),
                ('permission_description', models.TextField(blank=True)),
                ('permission_type', models.CharField(choices=[('USER', 'User Permission')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('abbr', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('project_description', models.TextField(blank=True, default='')),
                ('team_only', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='ProjectTeam',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('project_id', models.ForeignKey(to='API.Project', related_name='project_team')),
            ],
            options={
                'ordering': ('project_id',),
            },
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('permission', models.ForeignKey(to='API.Permission', related_name='users_with_permission')),
            ],
            options={
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='APIUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='userpermission',
            name='user',
            field=models.ForeignKey(to='API.APIUser', related_name='my_permissions'),
        ),
        migrations.AddField(
            model_name='projectteam',
            name='user_id',
            field=models.ForeignKey(to='API.APIUser', related_name='user_projects'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_manager',
            field=models.ForeignKey(to='API.APIUser', related_name='projects'),
        ),
        migrations.AddField(
            model_name='issueattachment',
            name='uploaded_by',
            field=models.ForeignKey(to='API.APIUser', related_name='my_attachments'),
        ),
        migrations.AddField(
            model_name='issue',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to='API.APIUser', related_name='my_opened_issues'),
        ),
        migrations.AddField(
            model_name='issue',
            name='created_by',
            field=models.ForeignKey(to='API.APIUser', related_name='my_created_issues'),
        ),
        migrations.AddField(
            model_name='issue',
            name='project_id',
            field=models.ForeignKey(to='API.Project', related_name='issues'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='API.APIUser', related_name='my_comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='issue_id',
            field=models.ForeignKey(to='API.Issue', related_name='comments'),
        ),
        migrations.AlterUniqueTogether(
            name='userpermission',
            unique_together=set([('user', 'permission')]),
        ),
    ]
