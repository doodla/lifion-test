from django.shortcuts import render

from lifion.models import Organization


def index(request):
    if request.user.is_authenticated:
        pass

    return render(request, 'lifion/index.html')


def login(request, user_id):
    pass


def record_response(request, survey_id):
    pass


def manage_question_bank(request):
    pass


def register(request):
    pass


def logout(request):
    pass


def organizations(request):
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
    return render(request, 'lifion/organizations.html', {
        'organizations': orgs,
        'orgs': True
    })
