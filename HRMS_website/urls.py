from django.conf.urls import url, include
from HRMS_website import views

urlpatterns = [
    url(r'^$', views.landing_page, name='index'),
    url(r'^base$', views.base, name='base'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^contact_form$', views.contact_form, name='base'),
    url(r'^update_issue/(?P<issue_id>\d+)', views.update_issue, name='update_issue'),
    url(r'^create_issue/', views.create_issue, name='create_issue'),
    url(r'^update_comment/(?P<comment_id>\d+)', views.update_comment, name='update_comment'),
    url(r'^add_work_log/', views.add_work_log, name='add_work_log'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^project/(?P<project_id>\d+)/', views.project, name='project_board'),
    url(r'^project_team/(?P<member_id>\d+)/', views.project_team, name='project_team'),
    url(r'^reports/', views.weekly_report, name='reports'),
    url(r'^weekly_report/', views.weekly_report, name='weekly_report'),
]