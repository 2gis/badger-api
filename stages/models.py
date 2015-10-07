from django.db import models
import datetime

from common.models import Project


class Stage(models.Model):
    name = models.CharField(max_length=128)
    project = models.ForeignKey(Project)
    text = models.TextField(default='', blank=True)
    link = models.URLField(default=None, blank=True, null=True)
    state = models.CharField(max_length=24, default='info', blank=True)
    weight = models.IntegerField(default=0)
    updated = models.DateTimeField(default=datetime.datetime.now())

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(Stage, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
