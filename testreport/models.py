from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from common.models import Project

from celery import states

import logging
import json

from django.conf import settings
import requests

log = logging.getLogger(__name__)

TEST_STATES = (PASSED, FAILED, SKIPPED, BLOCKED) = (0, 1, 2, 3)
LAUNCH_STATES = (INITIALIZED, IN_PROGRESS, FINISHED, STOPPED) = (0, 1, 2, 3)
LAUNCH_TYPES = (ASYNC_CALL, INIT_SCRIPT, CONCLUSIVE) = (0, 1, 2)
CELERY_FINISHED_STATES = (states.SUCCESS, states.FAILURE)


class ExtUser(models.Model):
    user = models.OneToOneField(User, related_name='settings')
    default_project = models.IntegerField(_('User default project'),
                                          blank=True, null=True, default=None)
    launches_on_page = models.IntegerField(_('Launches on page'), default=10)
    testresults_on_page = models.IntegerField(
        _('Testresults on page'), default=25)


class TestPlan(models.Model):
    name = models.CharField(_('Name'), max_length=256)
    project = models.ForeignKey(Project)
    main = models.BooleanField(_('Show in short statistic'),
                               blank=True, null=False, default=False)
    hidden = models.BooleanField(blank=False, null=False, default=True)
    owner = models.ForeignKey(User, default=1)
    filter = models.TextField(_('Started by filter'), default='',
                              blank=True, null=False, max_length=128)
    description = models.TextField(_('Description'), default='',
                                   blank=True, null=False)
    variable_name = models.TextField(_('Environment variable name'),
                                     default='', blank=True,
                                     null=False, max_length=128)
    variable_value_regexp = models.CharField(_('Regexp for variable value'),
                                             max_length=255, default='',
                                             blank=True)

    def __str__(self):
        return '{0} -> TestPlan: {1}'.format(self.project, self.name)


class Launch(models.Model):
    test_plan = models.ForeignKey(TestPlan)
    counts_cache = models.TextField(blank=True, null=True, default=None)
    started_by = models.URLField(_('Started by'), blank=True, null=True,
                                 default=None)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    finished = models.DateTimeField(_('Finished'), default=None, blank=True,
                                    null=True)
    state = models.IntegerField(_('State'), default=FINISHED)
    tasks = models.TextField(_('Tasks'), default='')
    parameters = models.TextField(_('Parameters'), default='{}')
    duration = models.FloatField(_('Duration time'), null=True, default=None)

    def is_finished(self):
        return self.state == FINISHED

    @property
    def counts(self):
        if self.counts_cache is None or self.state == INITIALIZED:
            self.calculate_counts()
        return json.loads(self.counts_cache)

    def calculate_counts(self):
        data = {
            'passed': len(self.passed),
            'failed': len(self.failed),
            'skipped': len(self.skipped),
            'blocked': len(self.blocked),
            'total': 0
        }
        for name, count in data.items():
            if name != 'total':
                data['total'] += count
        self.counts_cache = json.dumps(data)
        self.save()

    @property
    def failed(self):
        return self.testresult_set.filter(state=FAILED)

    @property
    def skipped(self):
        return self.testresult_set.filter(state=SKIPPED)

    @property
    def passed(self):
        return self.testresult_set.filter(state=PASSED)

    @property
    def blocked(self):
        return self.testresult_set.filter(state=BLOCKED)

    def get_tasks(self):
        if self.tasks == '' or self.tasks is None:
            self.tasks = '{}'
        return json.loads(self.tasks)

    def set_tasks(self, tasks):
        self.tasks = json.dumps(tasks)

    def get_parameters(self):
        if self.parameters == '' or self.parameters is None:
            self.parameters = '{}'
        return json.loads(self.parameters)

    def set_parameters(self, parameters):
        self.parameters = json.dumps(parameters)

    def __str__(self):
        return '{0} -> Launch: {1}'.format(self.test_plan, self.pk)


class TestResult(models.Model):
    launch = models.ForeignKey(Launch)
    name = models.CharField(_('Name'), max_length=128)
    suite = models.CharField(_('TestSuite'), max_length=256)
    state = models.IntegerField(_('State'), default=BLOCKED)
    failure_reason = models.TextField(_('Failure Reason'), default=None,
                                      blank=True, null=True)
    duration = models.FloatField(_('Duration time'), default=0.0)
    launch_item_id = models.IntegerField(blank=True, default=None, null=True)

    def __str__(self):
        return '{0} -> TestResult: {1}/{2}'.format(
            self.launch, self.suite, self.name)


class LaunchItem(models.Model):
    test_plan = models.ForeignKey(TestPlan)
    name = models.CharField(
        max_length=128, default=None, null=True, blank=True)
    command = models.TextField()
    timeout = models.IntegerField(default=300)
    type = models.IntegerField(default=ASYNC_CALL)

    def __str__(self):
        return '{0} -> {1}'.format(self.test_plan.name, self.name)


class Bug(models.Model):
    externalId = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, default='', blank=True)
    regexp = models.CharField(max_length=255, default='', blank=False)
    state = models.CharField(max_length=16, default='', blank=True)
    updated = models.DateTimeField(auto_now=True)

    def get_state(self):
        return self.state

    def __str__(self):
        return ':'.join((self.externalId, self.name))


def get_issue_fields_from_bts(externalId):
    log.debug('Get fields for bug {}'.format(externalId))
    res = _get_bug(externalId)
    if 'fields' in res:
        return res['fields']
    return res


def _get_bug(bug_id):
    response = requests.get(
        'https://{}{}'.format(
            settings.BUG_TRACKING_SYSTEM_HOST,
            settings.BUG_TRACKING_SYSTEM_BUG_PATH.format(issue_id=bug_id)),
        auth=(settings.BUG_TRACKING_SYSTEM_LOGIN,
              settings.BUG_TRACKING_SYSTEM_PASSWORD),
        headers={'Content-Type': 'application/json'})
    data = response.json()
    log.debug(data)
    return data
