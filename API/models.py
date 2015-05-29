from django.db import models
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.contrib.auth.models import User

STATUSES_ENUM = [
    ('OPENED', 'Opened'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESOLVED', 'Resolved'),
    ('CLOSED', 'Closed'),
]
TYPES_ENUM = [
    ('TASK', 'Task'),
    ('BUG', 'Bug'),
    ('SUB_TASK', 'Sub Task'),
]
LINKS_ENUM = [
    ('PARENT', 'Parent'),
    ('CHILD', 'Child'),
    ('RELATED_TO', 'Related to'),
    ('DUPLICATES', 'Duplicates'),
    ('BLOCKED_BY', 'Blocked by'),
]
PERMISSION_TYPE_ENUM = [
    ('USER', 'User Permission'),
]



class APIUser(User):
    class Meta:
        proxy = True

    def get_full_name_and_email(self):
        return "{} {}({})".strip().format(self.first_name, self.last_name, self.email) if \
            (self.first_name or self.last_name) else self.email

    def __str__(self):
        return self.get_full_name_and_email()



class Project(models.Model):
    class Meta:
        ordering = ('title',)

    abbr = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100, unique=True)
    project_description = models.TextField(blank=True, default='')
    team_only = models.BooleanField(default=False)
    project_manager = models.ForeignKey('APIUser', related_name='projects')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProjectTeam(models.Model):
    class Meta:
        ordering = ('project_id',)

    user_id = models.ForeignKey('APIUser', related_name='user_projects')
    project_id = models.ForeignKey('Project', related_name='project_team')

    def __str__(self):
        return self.user_id.get_full_name_and_email()


class Issue(models.Model):
    class Meta:
        ordering = ('project_id', 'created',)

    issue_key = models.CharField(max_length=10, unique=True)
    project_id = models.ForeignKey('Project', related_name='issues')
    title = models.CharField(max_length=100, unique=True)
    issue_description = models.TextField(blank=True, default='')
    status = models.CharField(choices=STATUSES_ENUM, default=STATUSES_ENUM[0], max_length=100)
    type = models.CharField(choices=TYPES_ENUM, default=TYPES_ENUM[0], max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('APIUser', related_name='my_created_issues')
    assigned_to = models.ForeignKey('APIUser', related_name='my_opened_issues', blank=True)
    highlighted = models.TextField()

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name('rst')
        formatter = HtmlFormatter(style='native', full=True)
        self.highlighted = highlight(self.issue_description, lexer, formatter)
        super(Issue, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self.title, self.issue_key)

class IssueAttachment(models.Model):
    class Meta:
        ordering = ('attachment_name', 'datetime_added')

    issue_id = models.ForeignKey('Issue', related_name='attachments')
    attachment_name = models.CharField(max_length=100)
    datetime_added = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="attachments")
    uploaded_by = models.ForeignKey('APIUser', related_name='my_attachments')


class IssueLink(models.Model):
    issue_id = models.ForeignKey('Issue', related_name='link_issue_id')
    link_type = models.CharField(choices=LINKS_ENUM, max_length=100)
    linked_issue_id = models.ForeignKey('Issue', related_name='linked_issue_id')

    def __str__(self):
        return "{} ({}) - {}".format(self.issue_id.issue_key, self.issue_id.title, self.link_type)

class Comment(models.Model):
    class Meta:
        ordering = ('issue_id', 'created',)
    issue_id = models.ForeignKey('Issue', related_name='comments')
    author = models.ForeignKey('APIUser', related_name='my_comments')
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(blank=True)
    highlighted = models.TextField()

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name('')
        formatter = HtmlFormatter(style=self.style, full=True)
        self.highlighted = highlight(self.comment, lexer, formatter)
        super(Comment, self).save(*args, **kwargs)


class Permission(models.Model):
    permission_name = models.CharField(max_length=100, blank=False, unique=True)
    permission_description = models.TextField(blank=True)
    permission_type = models.CharField(blank=False, choices=PERMISSION_TYPE_ENUM, max_length=30)

    def __str__(self):
        # return "%s | %s | %s" % (
        #     six.text_type(self.content_type.app_label),
        #     six.text_type(self.content_type),
        #     six.text_type(self.name))
        return "{}".format(self.permission_description)

class UserPermission(models.Model):
    user = models.ForeignKey('APIUser', related_name='my_permissions')
    permission = models.ForeignKey('Permission', related_name='users_with_permission')

    class Meta:
        ordering = ('user',)
        unique_together = ('user', 'permission')

    def __str__(self):
        return "{} {} - {}".format(
            self.user.first_name,
            self.user.last_name,
            self.permission.permission_description
        )
