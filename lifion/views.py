from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from lifion.models import Organization, LifionUser, Survey, Question, Option, Submission, QuestionBank, QuestionResponse


def index(request):
    if request.user.is_authenticated:
        pass

    return render(request, 'lifion/index.html', {'home': True})


def manage_organizations(request):
    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')

            organization = Organization.objects.create(name=name)

            QuestionBank.objects.create(organization=organization)

        elif action == 'delete':
            organization_id = request.POST.get('id')

            organization = Organization.objects.get(id=organization_id)
            organization.delete()

    orgs = Organization.objects.all()

    if not request.user.is_authenticated:
        return render(request, 'lifion/organizations.html', {
            'organizations': orgs,
            'orgs': True
        })
    return redirect('home')


def manage_employees(request):
    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'add':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            organization_id = request.POST.get('organization')

            user = LifionUser.objects.filter(username=username).first()

            if user is None:
                organization = Organization.objects.get(id=organization_id)

                user = LifionUser.objects.create(username=username,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 organization=organization)

                user.set_password('pass@123')
                user.save()
                messages.success(request, 'Successfully registered {}'.format(username))
            else:
                messages.error(request, 'User already exists. Please try with a different Username.')

        elif action == 'login':
            emp_id = request.POST.get('emp_id')

            user = LifionUser.objects.get(id=emp_id)

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            messages.success(request, 'Logged In as {} {}'.format(user.first_name, user.last_name))
            login(request, user)

    if not request.user.is_authenticated:
        orgs = Organization.objects.all()
        return render(request, 'lifion/employees.html', {
            'organizations': orgs,
            'emps': True
        })
    return redirect('survey')


def manage_surveys(request):
    if request.user.is_authenticated:

        user = request.user

        start = request.GET.get('start', None)
        end = request.GET.get('end', None)

        if start is not None:
            start = datetime.strptime(start, '%m-%d-%Y %H:%M')
            end = datetime.strptime(end, '%m-%d-%Y %H:%M')
            user_surveys = Survey.objects.filter(user=user, created_at__gte=start, created_at__lte=end).annotate(avg=Avg('submissions__responses__weighted_score'))
        else:
            user_surveys = Survey.objects.filter(user=user).annotate(avg=Avg('submissions__responses__weighted_score'))

        other_surveys = user.requested_surveys.filter()

        total = user_surveys.aggregate(Avg('avg')).get('avg__avg', 0)

        return render(request, 'lifion/survey/manage.html', {
            'user_surveys': user_surveys,
            'other_surveys': other_surveys,
            'total': total,
            'surves': True,
        })
    else:
        return redirect('home')


def take_survey(request, survey_id):
    if request.user.is_authenticated:

        survey = Survey.objects.get(id=survey_id)

        if request.method == 'POST':
            comment = request.POST.get('comment')
            check = request.POST.get('anonymous', None)
            options = request.POST.get('options').split(',')
            questions = request.POST.get('questions').split(',')

            if check is not None:
                anonymous = True
            else:
                anonymous = False

            submission = Submission.objects.create(user=request.user,
                                                   survey=survey,
                                                   anonymous=anonymous,
                                                   comment=comment)

            for pq, po in zip(questions, options):
                question = Question.objects.get(id=int(pq))
                option = Option.objects.get(id=int(po))

                max_val = question.options.aggregate(Max('value')).get('value__max')

                val = option.value

                weighted_score = (Decimal(val) / Decimal(max_val)) * 5

                QuestionResponse.objects.create(submission=submission,
                                                option=option,
                                                question=question,
                                                weighted_score=weighted_score)

            messages.success(request, 'Response submitted.')
            return redirect('survey')

        submission = Submission.objects.filter(survey=survey, user=request.user).first()

        if submission is not None:
            messages.error(request, 'You\'ve already submitted your response to this survey!')
            return redirect('survey')

        return render(request, 'lifion/survey/take.html', {
            'survey': survey,
            'surves': True,
        })
    else:
        return redirect('home')


def view_survey(request, survey_id):
    survey = Survey.objects.filter(id=survey_id).first()

    if survey is not None:
        html = render_to_string('lifion/survey/view.html', {'survey': survey})
        return HttpResponse(html)


def view_response(request, survey_id, submission_id):
    survey = Survey.objects.filter(id=survey_id).first()

    submission = Submission.objects.get(id=submission_id)
    if survey is not None:
        html = render_to_string('lifion/survey/response_view.html', {'survey': survey,
                                                                     'submission': submission})
        return HttpResponse(html)


def create_survey(request):
    if request.user.is_authenticated:

        user = request.user
        if request.method == 'POST':
            questions = request.POST.get('questions')
            submitters = request.POST.getlist('submitters')

            survey = Survey.objects.create(
                user=user,
                organization=user.organization,
            )

            questions = list(set(questions.split(',')))
            for pk in questions:
                question = Question.objects.get(id=int(pk))
                survey.questions.add(question)

            for pk in submitters:
                submitter = LifionUser.objects.get(id=int(pk))
                survey.submitters.add(submitter)

            survey.save()

            return redirect('survey')

        survey = Survey.objects.filter(user=user, is_open=True).first()
        question_bank = user.organization.question_bank
        if survey is not None:
            messages.error(request, 'You can only have one survey open at a time.')
            return redirect('survey')

        if user.organization.employees.all().count() == 1:
            messages.error(request, 'You\'re the only employee in your organization! Who\'s the survey for?')
            return redirect('survey')

        return render(request, 'lifion/survey/create.html', {
            'surves': True,
            'question_bank': question_bank,
        })
    else:
        return redirect('home')


def delete_survey(request, survey_id):
    if request.user.is_authenticated:

        survey = Survey.objects.filter(id=survey_id).first()

        if survey is not None:
            survey.delete()
            messages.success(request, 'Successfully deleted survey.')
        else:
            messages.error(request, 'Survey not found!')

        return redirect('survey')

    else:
        return redirect('home')


def survey_response(request, survey_id):
    if request.user.is_authenticated:

        survey = Survey.objects.filter(id=survey_id).first()

        avg = survey.submissions.aggregate(Avg('responses__weighted_score')).get('responses__weighted_score__avg',0)

        if survey is not None:

            return render(request, 'lifion/survey/response.html', {
                'surves': True,
                'survey': survey,
                'avg': avg
            })

        else:
            messages.error(request, 'Survey not found!')

        return redirect('survey')

    else:
        return redirect('home')


def close_survey(request):
    if request.user.is_authenticated:

        survey = Survey.objects.filter(user=request.user, is_open=True).first()

        if survey is not None:
            survey.is_open = False
            survey.save()
            messages.success(request, 'Successfully closed survey.')
        else:
            messages.error(request, 'Open Survey not found!')

        return redirect('survey')

    else:
        return redirect('home')


def view_question_bank(request):
    orgs = Organization.objects.all()

    return render(request, 'lifion/question_bank/view.html', {
        'bank': True,
        'organizations': orgs,
    })


def manage_question_bank(request, organization_id):
    org = Organization.objects.get(id=organization_id)

    return render(request, 'lifion/question_bank/manage.html', {
        'bank': True,
        'organization': org,
    })


@require_POST
def create_question(request):
    q_text = request.POST.get('q_text')
    texts = request.POST.getlist('text')
    values = request.POST.getlist('points')

    # Create the question
    question = Question.objects.create(text=q_text)

    for text, value in zip(texts, values):
        Option.objects.create(text=text,
                              value=int(value),
                              question=question)

    return JsonResponse({
        'success': True,
        'q_id': question.id,
    })


def logout_user(request):
    logout(request)
    messages.success(request, 'Logged Out!')
    return redirect('employees')


@require_POST
def add_question_to_bank(request, organization_id):
    questions = request.POST.get('questions')
    organization = Organization.objects.get(id=organization_id)

    question_bank = organization.question_bank
    for pk in questions.split(','):
        question = Question.objects.get(id=int(pk))
        question_bank.questions.add(question)

    question_bank.save()

    return redirect('manage_question_bank', organization_id=organization_id)


def remove_question_from_bank(request, organization_id, question_id):
    question = Question.objects.get(id=question_id)
    question_bank = QuestionBank.objects.get(organization=Organization.objects.get(id=organization_id))

    question_bank.questions.remove(question)
    question_bank.save()

    return redirect('manage_question_bank', organization_id=organization_id)
