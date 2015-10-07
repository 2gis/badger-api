from django.core.management.base import BaseCommand, CommandError

from testreport.models import Launch
from testreport.models import TestPlan
from testreport.models import TestResult
from testreport.models import PASSED, FAILED, BLOCKED, SKIPPED

from common.models import Project

from optparse import make_option

import os
import xml.dom.minidom
import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--project-name',
                    help='Name of the project for import'),
        make_option('--test-plan-name',
                    help='Name of the testplan for import'),
        make_option('--launch-id',
                    default=None,
                    help='Launch id'),
        make_option('--started-by',
                    default=None,
                    help='Url to web service which start launch'),
        make_option('--save',
                    action='store_true',
                    default=False,
                    help='Launch id')
    )
    launch = None
    buffer = []

    def handle(self, *args, **options):
        if options['project_name'] is None:
            raise CommandError('--project-name is not specified')
        if options['test_plan_name'] is None:
            raise CommandError('--test-plan-name is not specified')
        if options['started_by'] is None:
            raise CommandError('--started-by is not specified')

        (project, new) = Project.objects.get_or_create(
            name=options['project_name'])
        (test_plan, new) = TestPlan.objects.get_or_create(
            name=options['test_plan_name'], project=project)
        if options['launch_id'] is None:
            self.launch = Launch(test_plan=test_plan,
                                 started_by=options['started_by'])
            if options['save']:
                self.launch.save()
                log.info('REPORT_URL=http://autotests.cd.test/launch/{0}/'.
                         format(self.launch.id))
        else:
            log.info('Try to get launch with id = %s', options['launch_id'])
            self.launch = Launch.objects.get(id=options['launch_id'])
        log.info('Using next launch: %s', self.launch)

        for file_path in args:
            self.load_file(file_path, self.launch)
        if options['save']:
            TestResult.objects.bulk_create(self.buffer)
            if self.launch.counts['failed'] > 0:
                log.info('BUILD_IS_UNSTABLE')

    def load_file(self, file_path, launch):
        if os.stat(file_path)[6] == 0:
            return
        log.info('Loading "%s"', file_path)
        dom = xml.dom.minidom.parse(file_path)
        self.parse(dom)

    def parse(self, element, path=''):
        if element.nodeName == 'testcase':
            self.create_test_result(element, path)
        if element.nodeName == 'testsuite':
            path += element.getAttribute('name') + '/'
        if element.hasChildNodes():
            for node in element.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    self.parse(node, path)

    def create_test_result(self, element, path):
        data = {
            'launch': self.launch,
            'name': element.getAttribute('name'),
            'suite': (path[:125] + '...') if len(path) > 125 else path,
            'state': BLOCKED,
            'duration': element.getAttribute('time'),
            'failure_reason': ''
        }
        error = self.get_node(element, ['error', 'failure'])
        skipped = self.get_node(element, ['skipped'])
        if skipped is not None:
            data['state'] = SKIPPED
            data['failure_reason'] = 'Type: {0} : {1}'.format(
                skipped.getAttribute('type'),
                self.get_text(skipped.childNodes))
        else:
            data['state'] = PASSED
        if error is not None:
            data['state'] = FAILED
            data['failure_reason'] = 'Type: {0} : {1}'.format(
                error.getAttribute('type'), self.get_text(error.childNodes))
        self.buffer.append(TestResult(**data))

    def get_node(self, element, names):
        for node in element.childNodes:
            if node.nodeName in names:
                return node
        return None

    def get_text(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data.encode('utf-8', errors='replace'))
        return ''.join(rc)
