from django.db import models
from django.utils.translation import ugettext as _


class Project(models.Model):
    name = models.CharField(_('Name'), max_length=128, unique=True)

    def __str__(self):
        return 'Project: {0}'.format(self.name)


class Settings(models.Model):
    project = models.ForeignKey(Project, related_name='settings')
    key = models.CharField(max_length=255)
    value = models.TextField()

    def __str__(self):
        return "{}={}".format(self.key, self.value)
