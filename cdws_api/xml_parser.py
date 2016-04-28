from testreport.models import Launch, TestResult, Build
from testreport.models import FINISHED
from testreport.models import PASSED, FAILED, SKIPPED, BLOCKED

from django.conf import settings

import datetime
import logging
import socket
import xml.dom.minidom
import json

log = logging.getLogger(__name__)


def get_launch(launch_id):
    return Launch.objects.get(id=launch_id)


def create_launch(plan_id):
    launch = Launch.objects.create(
        test_plan_id=plan_id, state=FINISHED,
        started_by='http://{}'.format(socket.getfqdn()),
        finished=datetime.datetime.now())
    return launch


class XmlParser:
    buffer = []
    launch_id = None
    buffer_size = 100
    total_duration = 0

    def __init__(self, launch_id):
        self.launch_id = launch_id

    def load_string(self, file_content):
        log.info('Loading file_content')
        dom = xml.dom.minidom.parseString(file_content)
        self.parse(dom)

    def get_node(self, element, names):
        for node in element.childNodes:
            if node.nodeName in names:
                return node
        return None

    def get_text(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE \
                    or node.nodeType == node.CDATA_SECTION_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def update_duration(self, launch):
        log.info('Updating total duration for launch {}'.format(launch.id))
        if launch.duration is None:
            launch.duration = self.total_duration
        launch.save()


class JunitParser(XmlParser):
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
        result = TestResult.objects.create(launch_id=self.launch_id)
        duration = element.getAttribute('time')

        if duration == '':
            result.duration = 0
        else:
            result.duration = duration
        self.total_duration += float(result.duration)

        result.name = element.getAttribute('name')[:127]
        result.suite = path[:125]
        result.state = BLOCKED
        result.failure_reason = ''

        failure = self.get_node(element, ['failure'])
        error = self.get_node(element, ['error'])
        skipped = self.get_node(element, ['skipped'])
        if skipped is not None:
            result.state = SKIPPED
            result.failure_reason = self.get_text(skipped.childNodes)
        elif failure is not None:
            result.state = FAILED
            result.failure_reason = self.get_text(failure.childNodes)
        elif error is not None:
            result.failure_reason = self.get_text(error.childNodes)
        else:
            result.state = PASSED

        if not element.getAttribute('format'):
            system_out = self.get_node(element, 'system-out')
            if system_out is not None:
                result.failure_reason += self.get_text(system_out.childNodes)

        result.save()


class NunitParser(XmlParser):
    def parse(self, element, path=''):
        if element.nodeName == 'test-case':
            self.create_test_result(element)
        if element.hasChildNodes():
            for node in element.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    self.parse(node, path)

    def create_test_result(self, element):
        result = TestResult.objects.create(launch_id=self.launch_id)
        result.state = BLOCKED
        result.failure_reason = ''
        duration = element.getAttribute('time')

        if duration == '':
            result.duration = 0
        else:
            result.duration = duration
        self.total_duration += float(result.duration)

        if element.getAttribute('result') in ['Ignored', 'Inconclusive']:
            if element.getAttribute('result') == 'Ignored':
                result.state = SKIPPED
            if element.getAttribute('result') == 'Inconclusive':
                result.state = BLOCKED
            reason = self.get_node(element, ['reason'])
            message = self.get_node(reason, ['message'])
            result.failure_reason = self.get_text(message.childNodes)

        if element.getAttribute('result') in ['Failure', 'Error']:
            if element.getAttribute('result') == 'Failure':
                result.state = FAILED
            if element.getAttribute('result') == 'Error':
                result.state = BLOCKED
            failure = self.get_node(element, ['failure'])
            message = self.get_node(failure, ['message'])
            trace = self.get_node(failure, ['stack-trace'])
            failure_reason = self.get_text(message.childNodes)
            if trace is not None and self.get_text(trace.childNodes) != '':
                failure_reason += '\n\nStackTrace:\n'
                failure_reason += self.get_text(trace.childNodes)
            result.failure_reason = failure_reason

        if element.getAttribute('result') == 'Success':
            result.state = PASSED

        result.name = element.getAttribute('name')[:127]
        result.save()


def xml_parser_func(format, file_content, launch_id, params):
    launch = get_launch(launch_id)
    if params is not None and launch.parameters == '{}':
        launch.parameters = params
        params_json = json.loads(params)
        if 'options' in params_json \
                and params_json['options']['started_by'] != '':
            if params_json['options'].get('duration') is not None:
                launch.duration = float(params_json['options']['duration'])
            launch.started_by = params_json['options']['started_by']

            commits = params_json['options'].get('last_commits')
            if commits is not None \
                    and len(commits) > settings.LAST_COMMITS_SIZE:
                commits = commits[:settings.LAST_COMMITS_SIZE]

            build_hash = params_json['options'].get('hash')
            if build_hash is None and commits is not None:
                build_hash = commits[0]

            build = Build(
                launch=launch,
                version=params_json['options'].get('version'),
                branch=params_json['options'].get('branch'),
                hash=build_hash,
                commit_message=params_json['options'].get('commit_message'),
                commit_author=params_json['options'].get('commit_author'))
            build.set_last_commits(commits)
            build.save()

    if format == 'nunit':
        parser = NunitParser(launch.id)
    elif format == 'junit':
        parser = JunitParser(launch.id)

    parser.load_string(file_content)
    parser.update_duration(launch)
