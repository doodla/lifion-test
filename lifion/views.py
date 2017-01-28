from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from lifion.models import Organization, LifionUser, Survey, Question, Option


def index(request):
    if request.user.is_authenticated:
        pass

    return render(request, 'lifion/index.html')


def record_response(request, survey_id):
    pass


def manage_question_bank(request):
    pass


def manage_organizations(request):
    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')

            organization = Organization.objects.create(name=name)

        elif action == 'delete':
            id = request.POST.get('id')

            organization = Organization.objects.get(id=id)
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
    return redirect('home')


def manage_surveys(request):
    if request.user.is_authenticated:

        user = request.user

        organization = request.user.organization

        user_surveys = Survey.objects.filter(user=user)

        other_surveys = Survey.objects.filter(organization=organization, is_open=True).exclude(user=user)

        return render(request, 'lifion/survey/manage.html', {
            'user_surveys': user_surveys,
            'other_surveys': other_surveys,
            'surves': True
        })
    else:
        return redirect('home')


def create_survey(request):
    if request.user.is_authenticated:

        user = request.user
        if request.method == 'POST':
            questions = request.POST.getlist('questions')

            survey = Survey.objects.create(
                user=user,
                organization=user.organization,
            )

            for pk in questions:
                question = Question.objects.get(id=pk)

                survey.questions.add(question)

            return redirect('survey')

        survey = Survey.objects.filter(user=user, is_open=True).first()

        if survey is not None:
            messages.error(request, 'You can only have one survey open at a time.')
            return redirect('survey')

        return render(request, 'lifion/survey/create.html', {
            'surves': True
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


@require_POST
def create_question(request):
    q_text = request.POST.get('q_text')
    texts = request.POST.getlist('text')
    values = request.POST.getlist('points')

    # Create the question
    question = Question.objects.create(text=q_text)

    for text, value in zip(texts, values):
        Option.objects.create(text=text,
                              value=value,
                              question=question)

    return JsonResponse({
        'success': True,
        'q_id': question.id,
    })


def logout_user(request):
    logout(request)
    messages.success(request, 'Logged Out!')
    return redirect('employees')
