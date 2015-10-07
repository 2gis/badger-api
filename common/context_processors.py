from common.models import Project


def projects(request):
    return {'projects': Project.objects.all()}
