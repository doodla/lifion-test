from django.contrib import admin

from .models import Submission, LifionUser, Survey, Organization

admin.site.register(Submission)
admin.site.register(LifionUser)
admin.site.register(Survey)
admin.site.register(Organization)
