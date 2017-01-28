"""doodle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import lifion.views as views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='home'),
    url(r'^logout[/]$', views.logout_user, name='logout'),
    url(r'^organizations[/]$', views.manage_organizations, name='organizations'),
    url(r'^employees[/]$', views.manage_employees, name='employees'),
    url(r'^survey[/]$', views.manage_surveys, name='survey'),
    url(r'^survey/create[/]$', views.create_survey, name='create_survey'),
    url(r'^survey/delete/(?P<survey_id>[0-9]+)$', views.delete_survey, name='delete_survey'),
    url(r'^survey/take/(?P<survey_id>[0-9]+)[/]$', views.take_survey, name='take_survey'),
    url(r'^survey/view/(?P<survey_id>[0-9]+)$', views.view_survey, name='view_survey'),
    url(r'^survey/response/(?P<survey_id>[0-9]+)[/]$', views.survey_response, name='survey_responses'),
    url(r'^survey/close[/]$', views.close_survey, name='close_survey'),
    url(r'^questions/create[/]$', views.create_question, name='create_question'),
]

urlpatterns += staticfiles_urlpatterns()
