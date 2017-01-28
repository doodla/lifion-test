from django import template

from lifion.models import Submission

register = template.Library()


@register.filter
def has_submission(user, survey):
    submission = Submission.objects.filter(user=user, survey=survey).first()

    if submission is None:
        return False
    else:
        return True
