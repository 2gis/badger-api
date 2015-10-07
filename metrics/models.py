from django.db import models
from django.core.validators import MinValueValidator

from djcelery.models import PeriodicTask

from common.models import Project
from metrics.handlers import HANDLER_CHOICES

from django.utils import timezone


class Metric(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    query = models.TextField(default='', blank=True)
    schedule = models.ForeignKey(PeriodicTask)
    handler = models.CharField(max_length=128, choices=HANDLER_CHOICES)
    error = models.TextField(default='', blank=True)
    weight = models.IntegerField(default=1)

    def __unicode__(self):
        return '{} -> Metric: {}'.format(self.project, self.name)

    def get_schedule_as_cron(self):
        cron = self.schedule.crontab
        return '{} {} {} {} {}'.format(cron.minute, cron.hour,
                                       cron.day_of_month, cron.month_of_year,
                                       cron.day_of_week)


class MetricValue(models.Model):
    metric = models.ForeignKey(Metric)
    value = models.FloatField(default=None,
                              validators=[MinValueValidator(0.0)])
    created = models.DateTimeField()

    def __unicode__(self):
        return self.value

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.created is None:
            self.created = timezone.now()
        super().save(force_insert, force_update, using, update_fields)
