from django.db import models
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from HRMS.settings import API_BASE_LINK


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
TEAM_ROLE_ENUM = [
    ('DEV', 'Developer'),
    ('QA', 'QA Engineer'),
    ('QALEAD', 'QA Team Lead'),
    ('PM', 'Project Manager'),
]
PRIORITY_ENUM=[
    ('TRIVIAL', 'Trivial'),
    ('MINOR', 'Minor'),
    ('MAJOR', 'Major'),
    ('CRITICAL', 'Critical'),
    ('BLOCKER', 'Blocker'),
]


class APIUser(User):
    class Meta:
        proxy = True

    def get_full_name_and_email(self):
        return "{} {}".strip().format(self.first_name, self.last_name) if \
            (self.first_name or self.last_name) else self.username

    def __str__(self):
        return self.get_full_name_and_email()


class Project(models.Model):
    class Meta:
        ordering = ('title',)

    abbr = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100, unique=True)
    project_description = models.TextField(blank=True, default='')
    project_manager = models.ForeignKey('APIUser', related_name='projects')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Project)
def add_project_manager(sender, **kwargs):
    project = kwargs['instance']
    project_manager=dict(
        project=project,
        user=project.project_manager,
        team_role='PM',
    )
    ProjectTeam.objects.create(**project_manager)


class ProjectTeam(models.Model):
    class Meta:
        ordering = ('project', 'id',)
        unique_together = ('project', 'user',)

    user = models.ForeignKey('APIUser', related_name='user_projects')
    project = models.ForeignKey('Project', related_name='project_team')
    team_role = models.CharField(choices=TEAM_ROLE_ENUM, default=TEAM_ROLE_ENUM[0], max_length=50)
    def __str__(self):
        return "{} - {}".format(self.user, dict(TEAM_ROLE_ENUM)[self.team_role])


class Issue(models.Model):
    class Meta:
        ordering = ('project_id', 'created',)

    issue_key = models.CharField(max_length=10, unique=True)
    project = models.ForeignKey('Project', related_name='issues')
    title = models.CharField(max_length=100, unique=True)
    issue_description = models.TextField(blank=True, default='')
    status = models.CharField(choices=STATUSES_ENUM, default=STATUSES_ENUM[0], max_length=100)
    type = models.CharField(choices=TYPES_ENUM, default=TYPES_ENUM[0], max_length=100)
    priority = models.CharField(choices=PRIORITY_ENUM, default=PRIORITY_ENUM[2], max_length=100)
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
        return "{} - {}".format(self.issue_key, self.title)


class IssueAttachment(models.Model):
    class Meta:
        ordering = ('attachment_name', 'datetime_added')

    issue = models.ForeignKey('Issue', related_name='attachments')
    attachment_name = models.CharField(max_length=100)
    datetime_added = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="attachments")
    uploaded_by = models.ForeignKey('APIUser', related_name='my_attachments')


class IssueLink(models.Model):
    issue = models.ForeignKey('Issue', related_name='link_issue')
    link_type = models.CharField(choices=LINKS_ENUM, max_length=100)
    linked_issue = models.ForeignKey('Issue', related_name='linked_issue')

    def __str__(self):
        return "{} ({}) - {}".format(self.issue_id.issue_key, self.issue_id.title, self.link_type)


class Comment(models.Model):
    class Meta:
        ordering = ('issue', 'created',)
    issue = models.ForeignKey('Issue', related_name='issue_comments')
    author = models.ForeignKey('APIUser', related_name='my_comments')
    comment = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        print(args)
        print(kwargs)
        super(Comment, self).save(*args, **kwargs)


class Worklog(models.Model):
    class Meta:
        ordering = ('issue', 'work_date', 'user',)
    user = models.ForeignKey('APIUser', related_name='my_worklogs')
    issue = models.ForeignKey('Issue', related_name='issue_worklogs')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Worklog logging time')
    updated = models.DateTimeField(auto_now_add=True, verbose_name='Worklog updating time')
    work_date = models.DateField(auto_now_add=True)
    work_hours = models.IntegerField(default=0)
    work_minutes = models.IntegerField(default=0)
