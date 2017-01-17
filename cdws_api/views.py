from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins

from rest_framework_xml.renderers import XMLRenderer
from rest_framework.parsers import BaseParser, FileUploadParser
from defusedxml import ElementTree

from rest_framework.exceptions import ParseError

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.filters import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework_bulk import ListBulkCreateAPIView

from common.storage import get_s3_connection, get_or_create_bucket
from common.models import Project, Settings
from common.tasks import launch_process
from testreport.tasks import create_environment

from cdws_api.serializers import ProjectSerializer
from cdws_api.serializers import LaunchSerializer
from cdws_api.serializers import LaunchItemSerializer
from cdws_api.serializers import TestResultSerializer
from cdws_api.serializers import TestPlanSerializer
from cdws_api.serializers import AsyncResultSerializer
from cdws_api.serializers import CommentSerializer
from cdws_api.serializers import BugSerializer
from cdws_api.serializers import StageSerializer
from cdws_api.serializers import MetricSerializer, MetricValueSerializer

from testreport.models import TestPlan
from testreport.models import Launch
from testreport.models import Build
from testreport.models import TestResult
from testreport.models import LaunchItem
from testreport.models import Bug
from testreport.models import INITIALIZED, ASYNC_CALL, INIT_SCRIPT, CONCLUSIVE
from testreport.models import STOPPED, IN_PROGRESS, FINISHED
from testreport.models import get_issue_fields_from_bts

from stages.models import Stage

from metrics.models import Metric, MetricValue
from metrics.handlers import HANDLER_CHOICES
from metrics.tasks import restore_metric_values

from testreport.tasks import finalize_launch
from testreport.tasks import parse_xml

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q, Count

from comments.models import Comment

from djcelery.models import TaskMeta, CrontabSchedule, PeriodicTask

from celery.utils import uuid

from django.conf import settings
from pycd.celery import app

import datetime
import logging
import celery
import copy
import os
import socket


log = logging.getLogger(__name__)


class GetOrCreateViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def find_duplicate(self, serializer):
        raise Exception('Please take care about realization \
                        of find_duplicate for your instance')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # :INFO: In any trouble, ask v.reyder for next 2 lines
            self.object = self.find_duplicate(serializer)
            serializer = serializer.__class__(self.object)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK,
                            headers=headers)
        except ObjectDoesNotExist as e:
            log.debug(e)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)


class ProjectViewSet(GetOrCreateViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    model = Project

    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )

    def find_duplicate(self, serializer):
        return Project.objects.get(name=serializer.initial_data['name'])

    @detail_route(methods=['post'],
                  permission_classes=[DjangoModelPermissionsOrAnonReadOnly],
                  url_path='settings')
    def set_settings(self, request, pk=None):
        (settings, new) = Settings.objects.get_or_create(
            project=Project.objects.get(id=pk), key=request.data['key'])
        settings.value = request.data['value']
        settings.save()
        return Response(status=status.HTTP_201_CREATED, data={'message': 'ok'})

    @detail_route(methods=['post'],
                  permission_classes=[DjangoModelPermissionsOrAnonReadOnly],
                  url_path='settings/delete')
    def delete_settings(self, request, pk=None):
        settings = Settings.objects.filter(
            project=Project.objects.get(id=pk),
            key=request.data['key'], value=request.data['value'])
        settings.delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'ok'})


class TestPlanViewSet(GetOrCreateViewSet):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer
    model = TestPlan

    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('id', 'project', 'name')

    @list_route(methods=['get'])
    def custom_list(self, request, *args, **kwargs):
        if 'project_id__in' in request.GET \
                and request.GET['project_id__in'] != '':
            self.queryset = self.queryset.filter(
                project_id__in=request.GET['project_id__in'].split(','))
        if 'id__in' in request.GET and request.GET['id__in'] != '':
            self.queryset = self.queryset.filter(
                id__in=request.GET['id__in'].split(','))
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.id
        return super(TestPlanViewSet, self).create(request, *args, **kwargs)

    def find_duplicate(self, serializer):
        if 'name' not in serializer.initial_data \
                or 'project' not in serializer.initial_data:
            raise ObjectDoesNotExist
        return TestPlan.objects.get(
            name=serializer.initial_data['name'],
            project=serializer.initial_data['project'])

    @detail_route(methods=['post'],
                  permission_classes=[IsAuthenticatedOrReadOnly])
    def execute(self, request, pk=None):
        workspace_path = os.path.join(
            settings.CDWS_WORKING_DIR,
            timezone.now().strftime('%Y-%m-%d-%H-%M-%f'))
        post_data = request.data
        options = request.data['options']
        json_file = None
        if 'json_file' in post_data:
            json_file = post_data['json_file']

        test_plan = TestPlan.objects.get(pk=pk)

        # launch create
        launch = Launch(test_plan=test_plan,
                        started_by=options['started_by'],
                        state=INITIALIZED)
        launch.save()

        build = Build(launch=launch,
                      version=options.get('version'),
                      branch=options.get('branch'),
                      hash=options.get('hash'))
        build.save()

        # env create
        env = {'WORKSPACE':
               os.path.join(settings.CDWS_DEPLOY_DIR, workspace_path),
               'HOME':
               os.path.join(settings.CDWS_DEPLOY_DIR, workspace_path)}
        if 'env' in post_data:
            for key, value in iter(post_data['env'].items()):
                env[key] = value
        env['REPORT_API_URL'] = 'https://{0}/{1}'.format(
            settings.CDWS_API_HOSTNAME, settings.CDWS_API_PATH)
        # environment values should be string for exec
        env['TESTPLAN_ID'] = str(test_plan.id)
        env['LAUNCH_ID'] = str(launch.id)
        env['WORKSPACE_URL'] = 'http://{}/{}/'.format(
            settings.CELERY_HOST, workspace_path)

        # queryset create
        if 'launch_items' in post_data:
            try:
                launch_items = test_plan.launchitem_set.filter(
                    id__in=post_data['launch_items']).order_by('id')
            except (KeyError, ValueError) as e:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'message': '{}'.format(e)})
        else:
            launch_items = test_plan.launchitem_set.all().order_by('id')

        mapping = {}
        init_task = None
        async_tasks = []
        conclusive_tasks = []

        create_env_task = create_environment.subtask(
            [env, json_file], immutable=True, soft_time_limit=1200)
        final_task = finalize_launch.subtask(
            [launch.id], {}, soft_time_limit=3600, immutable=True)

        is_init_task_present = False
        for launch_item in launch_items:
            item_uuid = uuid()
            # Write LAUNCH_ITEM_ID to environment of each process
            item_env = copy.copy(env)
            item_env['LAUNCH_ITEM_ID'] = str(launch_item.id)
            subtask = launch_process.subtask(
                [launch_item.command, launch_item.type], {'env': item_env},
                immutable=True,
                soft_time_limit=launch_item.timeout,
                options={'task_id': item_uuid})

            if launch_item.type == INIT_SCRIPT:
                if not is_init_task_present:
                    is_init_task_present = True
                    init_task = subtask
                    mapping[item_uuid] = launch_item.id
            elif launch_item.type == ASYNC_CALL:
                async_tasks.append(subtask)
                mapping[item_uuid] = launch_item.id
            elif launch_item.type == CONCLUSIVE:
                conclusive_tasks.append(subtask)
                mapping[item_uuid] = launch_item.id
            else:
                msg = ('There is launch item with type {0} which not '
                       'supported, please fix this.').format(launch_item.type)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'message': msg})
        # update launch
        launch.set_tasks(mapping)
        launch.set_parameters({
            'options': options,
            'env': {} if 'env' not in post_data else post_data['env'],
            'json_file': json_file
        })
        launch.save()

        # error handling
        if init_task is None:
            msg = ('Initial script for test plan "{0}" with id "{1}" '
                   'does not exist or not selected. '
                   'Currently selected items: {2}').format(
                test_plan.name, test_plan.id, launch_items)
            launch.delete()
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': msg})
        # pass sequence
        sequence = [create_env_task, init_task, celery.group(async_tasks)]
        sequence += conclusive_tasks
        sequence.append(final_task)

        try:
            log.info("Chain={}".format(celery.chain(sequence)()))
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={'message': '{}'.format(e)})

        return Response(data={'launch_id': launch.id},
                        status=status.HTTP_200_OK)


class LaunchViewSet(viewsets.ModelViewSet):
    queryset = Launch.objects.all()
    serializer_class = LaunchSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('test_plan', 'id', 'created', 'state',
                     'build__version', 'build__hash', 'build__branch')
    search_fields = ('started_by',)

    @detail_route(methods=['get'],
                  permission_classes=[IsAuthenticatedOrReadOnly])
    def terminate_tasks(self, request, pk=None):
        try:
            launch = Launch.objects.get(id=pk)
            tasks = {}
            for key, v in iter(launch.get_tasks().items()):
                # Don't save tasks with status PENDING, due PENDING mean
                # unknown status too.
                if app.AsyncResult(key).state != 'PENDING':
                    tasks[key] = v
                app.control.revoke(key, terminate=True, signal='SIGTERM')
            launch.set_tasks(tasks)
            launch.save()
            finalize_launch(pk, STOPPED)
        except Launch.DoesNotExist:
            return Response(
                data={
                    'message': 'Launch with id={} does not exist'.format(pk)},
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={
                    'message': 'Unable to terminate tasks for launch id={},'
                               ' due to {}'.format(pk, e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            data={'message': 'Termination done.'},
            status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def custom_list(self, request, *args, **kwargs):
        if 'days' in request.GET:
            delta = datetime.datetime.today() - datetime.timedelta(
                days=int(request.GET['days']))
            self.queryset = self.queryset.filter(created__gt=delta)
        if 'testplan_id__in' in request.GET \
                and request.GET['testplan_id__in'] != '':
            self.queryset = self.queryset.filter(
                test_plan_id__in=request.GET['testplan_id__in'].split(','))
        if 'from' in request.GET:
            from_date = request.GET['from']
            to_date = datetime.datetime.today()
            if 'to' in request.GET:
                to_date = request.GET['to']
            self.queryset = self.queryset.filter(
                created__range=(from_date, to_date))
        if 'build_hash__in' in request.GET \
                and request.GET['build_hash__in'] != '':
            self.queryset = self.queryset.filter(
                build__hash__in=request.GET['build_hash__in'].split(','))
        if 'results_group_count' in request.GET \
                and request.GET['results_group_count'] != '':
            launch = Launch.objects.get(id=request.GET['results_group_count'])

            results = TestResult.objects.\
                filter(launch=launch, state=request.GET['state']).\
                values('launch_item_id').\
                annotate(count=Count('launch_item_id'))
            return Response(data={'results': results},
                            status=status.HTTP_200_OK)
        return self.list(request, *args, **kwargs)

    @detail_route(methods=['get'],
                  permission_classes=[IsAuthenticatedOrReadOnly])
    def calculate_counts(self, request, pk=None):
        try:
            Launch.objects.get(id=pk).calculate_counts()
        except Launch.DoesNotExist:
            return Response(
                data={
                    'message': 'Launch with id {} does not exist'.format(pk)},
                status=status.HTTP_404_NOT_FOUND)
        return Response(
            data={'message': 'Calculation done.'},
            status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  permission_classes=[IsAuthenticatedOrReadOnly])
    def update_metrics(self, request, pk=None):
        if 'metrics' in request.data and request.data['metrics'] != '':
            if type(request.data['metrics']) is not dict:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'message': 'Invalid format for metrics \'{0}\','
                        ' expect object'.format(request.data['metrics'])})
            try:
                launch = Launch.objects.get(id=pk)
                params = launch.get_parameters()
                params['metrics'] = request.data['metrics']
                launch.set_parameters(params)
                launch.save()
                return Response(status=status.HTTP_200_OK,
                                data=LaunchSerializer(launch).data)
            except Launch.DoesNotExist:
                return Response(
                    data={'message':
                          'Launch with id={} does not exist'.format(pk)},
                    status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'message': 'No metrics in post request: '
                                         '{0}'.format(request.data)})


class TestResultViewSet(ListBulkCreateAPIView,
                        viewsets.GenericViewSet,
                        mixins.RetrieveModelMixin):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    model = TestResult
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('$suite', '$name', '$failure_reason')
    filter_fields = ('id', 'state', 'name', 'launch',
                     'duration', 'launch_item_id')

    @list_route(methods=['get'])
    def custom_list(self, request, *args, **kwargs):
        days = 100
        if 'launch_id__in' in request.GET \
                and request.GET['launch_id__in'] != '':
            self.queryset = self.queryset.filter(
                launch_id__in=request.GET['launch_id__in'].split(','))
        if 'state__in' in request.GET and request.GET['state__in'] != '':
            self.queryset = self.queryset.filter(
                state__in=request.GET['state__in'].split(','))
        if 'days' in request.GET and request.GET['days'] != '':
            days = int(request.GET['days'])
        if 'history' in request.GET and request.GET['history'] != '':
            result = TestResult.objects.get(id=request.GET['history'])
            launch = Launch.objects.get(id=result.launch_id)
            delta = datetime.datetime.today() - datetime.timedelta(days=days)
            launches = Launch.objects.filter(
                test_plan_id=launch.test_plan_id, created__gt=delta)

            ids = []
            for l in launches:
                ids.append(l.id)

            self.queryset = self.queryset.\
                filter(launch_id__in=ids).\
                filter(name=result.name, suite=result.suite).\
                order_by('-launch')
        return self.list(request, *args, **kwargs)


class TestResultNegativeViewSet(TestResultViewSet):
    search_fields = ('$failure_reason', )


class LaunchItemViewSet(viewsets.ModelViewSet):
    queryset = LaunchItem.objects.all()
    serializer_class = LaunchItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('id', 'name', 'test_plan', 'type')


class TaskResultViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = AsyncResultSerializer
    queryset = TaskMeta.objects.all()

    def retrieve(self, request, *args, **kwargs):
        log.info(kwargs)
        serializer = self.get_serializer(
            launch_process.AsyncResult(kwargs['pk']))
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('id', 'user', 'content_type', 'object_pk')

    def create(self, request, *args, **kwargs):
        ct = ContentType.objects.get(name__exact=request.data['content_type'])
        request.data['content_type'] = ct.id
        request.data['user'] = request.user.id
        return super(CommentViewSet, self).create(request, *args, **kwargs)


class BugViewSet(viewsets.ModelViewSet):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, OrderingFilter, )
    filter_fields = ('id', 'externalId')

    def create(self, request, *args, **kwargs):
        log.info('Check issue {} for existing'.
                 format(request.data['externalId']))
        response = get_issue_fields_from_bts(request.data['externalId'])

        errors = []
        if 'errors' in response:
            errors += response['errors']
        if 'errorMessages' in response:
            errors += response['errorMessages']
        if len(errors) != 0:
            return Response(
                data={'message': '\n'.join(errors)},
                status=status.HTTP_400_BAD_REQUEST)

        Bug.objects.create(externalId=request.data['externalId'],
                           regexp=request.data['regexp'],
                           state=response['status']['name'],
                           name=response['summary'])
        return Response(status=status.HTTP_201_CREATED)

    @list_route(methods=['get'])
    def custom_list(self, request, *args, **kwargs):
        if 'issue_names__in' in request.GET \
                and request.GET['issue_names__in'] != '':
            issue_names = request.GET['issue_names__in'].split(',')
            query = Q()
            for issue_name in issue_names:
                query = query | Q(externalId__startswith=issue_name)
            self.queryset = Bug.objects.filter(query)

        return self.list(request, *args, **kwargs)


class StageViewSet(GetOrCreateViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('id', 'project')

    def find_duplicate(self, serializer):
        return Stage.objects.get(
            name=serializer.init_data['name'],
            project=serializer.init_data['project'])


class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class JenkinsViewSet(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)

    def post(self, request, format=None, project=None):
        name = request.data['name']
        build_phase = request.data['build']['phase']
        build_full_url = request.data['build']['full_url']

        try:
            project = Project.objects.get(name=project)
        except ObjectDoesNotExist:
            return Response(
                data={'message': 'Project {0} does not exist'.format(project)},
                status=status.HTTP_404_NOT_FOUND)

        try:
            build_number = Settings.objects.get(
                project=project, key='current_build').value
        except ObjectDoesNotExist:
            build_number = ''

        log.debug(build_number)
        (stage, new) = Stage.objects.get_or_create(
            name=name, project=project)

        stage.link = build_full_url
        stage.state = self._get_build_state(request.data)
        if build_number != '':
            stage.text = '{0} (build {1})'.format(build_phase, build_number)
        else:
            stage.text = '{0}'.format(build_phase)
        stage.save()

        return Response(data={'message': 'Done.'},
                        status=status.HTTP_201_CREATED)

    def _get_build_state(self, data):
        if 'status' not in data['build']:
            return 'warning'
        status = data['build']['status']
        if status == 'SUCCESS':
            return 'success'
        elif status == 'FAILURE':
            return 'danger'
        else:
            return 'warning'


class CustomXmlParser(BaseParser):
    media_type = 'text/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as XML and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', 'utf-8')
        parser = ElementTree.DefusedXMLParser(encoding=encoding)
        try:
            tree = ElementTree.parse(stream, parser=parser, forbid_dtd=True)
        except (ElementTree.ParseError, ValueError) as e:
            raise ParseError('XML parse error - {}'.format(e))
        return tree.getroot()


class RundeckViewSet(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    renderer_classes = (XMLRenderer,)
    parser_classes = (CustomXmlParser, )

    def post(self, request, format=None, project=None):
        root = request.data
        job_status = 'unknown'
        group_name = 'unknown'
        href = settings.RUNDECK_URL
        for child in root.iter():
            if child.tag == 'execution':
                job_status = child.attrib['status']
                href = child.attrib['href']
            elif child.tag == 'job':
                for group in child.iter('group'):
                    group_name = group.text

        try:
            project = Project.objects.get(name=project)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            build_number = Settings.objects.get(
                project=project, key='current_build').value
        except ObjectDoesNotExist:
            build_number = ''

        (stage, new) = Stage.objects.get_or_create(
            name=group_name, project=project)

        stage.link = href
        stage.state = self._get_build_state(job_status)
        if build_number != '':
            stage.text = '{0} (build {1})'.format(
                job_status.upper(), build_number)
        else:
            stage.text = '{}'.format(job_status.upper())
        # if job_status != 'succeeded':
        #     stage.text = '%s, AVG %s sec. (build %s)' %
        # (job_status, float(duration) / 1000, build_number, )
        stage.save()
        return Response(data={'message': 'Done.'},
                        status=status.HTTP_201_CREATED)

    def _get_build_state(self, status):
        if status == 'succeeded':
            return 'success'
        elif status == 'failed':
            return 'danger'
        else:
            return 'warning'


class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    filter_backends = (DjangoFilterBackend, OrderingFilter, )
    filter_fields = ('project', )

    def crontab_create(self, schedule):
        cron_template = schedule.split()
        (crontab, new) = CrontabSchedule.objects.get_or_create(
            minute=cron_template[0],
            hour=cron_template[1],
            day_of_month=cron_template[2],
            month_of_year=cron_template[3],
            day_of_week=cron_template[4]
        )
        return crontab

    def create(self, request, *args, **kwargs):
        if 'project' not in request.data:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': 'Field "project" is required'})
        if 'name' not in request.data or request.data['name'] == '':
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': 'Field "name" is required'})
        if not any(request.data['handler'] in choice
                   for choice in HANDLER_CHOICES):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': 'Handler "{}" is not a valid choice'
                      .format(request.data['handler'])})
        project = Project.objects.get(pk=request.data['project'])
        crontab = self.crontab_create(request.data['schedule'])

        periodic_task = PeriodicTask.objects.create(
            name=uuid(),
            task='metrics.tasks.run_metric_calculation',
            crontab_id=crontab.id,
            enabled=True
        )

        message = {'message': 'Metric already exist, choose another name'}
        try:
            Metric.objects.get(project=project, name=request.data['name'])
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=message)
        except ObjectDoesNotExist:
            metric = Metric.objects.create(
                name=request.data['name'],
                project=project,
                schedule=periodic_task,
                query=request.data['query'],
                handler=request.data['handler'],
                weight=request.data['weight'],
            )
            periodic_task.args = [metric.id]
            periodic_task.save()

            if 'query_period' in request.data:
                restore_metric_values.apply_async(args=[
                    metric.id,
                    request.data['query_period'],
                    request.data['query_step'],
                    request.data['handler'],
                    request.data['query_field']])

            return Response(status=status.HTTP_201_CREATED,
                            data=MetricSerializer(metric).data)
        except MultipleObjectsReturned:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=message)
        except Exception as e:
            log.error(e)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={'message': e})

    def update(self, request, pk=None, *args, **kwargs):
        try:
            metric = Metric.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'message': 'Metric not found'})

        if 'schedule' in request.data:
            crontab = self.crontab_create(request.data['schedule'])
            periodic_task = PeriodicTask.objects.get(id=metric.schedule_id)
            periodic_task.crontab_id = crontab.id
            periodic_task.save()
            request.data['schedule'] = periodic_task.id

        message = {'message': 'Metric already exist, choose another name'}
        try:
            Metric.objects.exclude(pk=metric.id)\
                .get(project=metric.project_id, name=request.data['name'])
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=message)
        except ObjectDoesNotExist:
            return super(MetricViewSet, self).update(request, *args, **kwargs)
        except MultipleObjectsReturned:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=message)
        except Exception as e:
            log.error(e)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={'message': e})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        PeriodicTask.objects.get(pk=instance.schedule_id).delete()

        return Response(
            status=status.HTTP_200_OK,
            data={'message': 'Metric and all values deleted'})


class MetricValueViewSet(viewsets.ModelViewSet):
    queryset = MetricValue.objects.all()
    serializer_class = MetricValueSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, )
    filter_fields = ('metric_id', )

    @list_route(methods=['get'])
    def custom_list(self, request, *args, **kwargs):
        if 'days' in request.GET:
            delta = datetime.datetime.today() - datetime.timedelta(
                days=int(request.GET['days']))
            self.queryset = self.queryset.filter(created__gt=delta)
        if 'from' in request.GET:
            from_date = request.GET['from']
            to_date = datetime.datetime.today()
            if 'to' in request.GET:
                to_date = request.GET['to']
            self.queryset = self.queryset.filter(
                created__range=(from_date, to_date))
        return self.list(request, *args, **kwargs)


class UnsafeBasicAuthentication(BasicAuthentication):
    def enforce_csrf(self, request):
        return


class ReportFileViewSet(APIView):
    authentication_classes = (UnsafeBasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, )
    parser_classes = (FileUploadParser,)

    def get_launch(self, launch_id):
        return Launch.objects.get(id=launch_id)

    def create_launch(self, plan_id, state):
        launch = Launch.objects.create(
            test_plan_id=plan_id, state=state,
            started_by='http://{}'.format(socket.getfqdn()))
        return launch

    def post(self, request, filename, testplan_id=None, xunit_format=None):
        s3_connection = get_s3_connection()
        file_obj = request.data['file']

        launch_id = None
        params = None
        if xunit_format not in ['junit', 'nunit']:
            return Response(data={'message': 'Unknown file format'},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'file' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'No file or empty file received'})
        if 'launch' in request.data:
            launch_id = request.data['launch']
        if 'data' in request.data:
            if isinstance(request.data['data'], InMemoryUploadedFile):
                params = request.data['data'].read().decode('utf8')
            elif request.data['data'] != '':
                params = request.data['data']

        log.info('Create launch')
        if testplan_id is not None:
            state = IN_PROGRESS if s3_connection is not None else FINISHED
            if launch_id is not None:
                launch = self.get_launch(launch_id)
            else:
                launch = self.create_launch(testplan_id, state=state)

            if s3_connection is not None:
                bucket = get_or_create_bucket(s3_connection)
                report_key = bucket.new_key(uuid())
                report_key.set_contents_from_string(file_obj.read())

                log.debug('Xml file "{}" created in bucket "{}"'.format(
                    report_key.name, settings.S3_BUCKET_NAME))

                parse_xml.apply_async(kwargs={'s3_conn': True,
                                              's3_key_name': report_key.name,
                                              'xunit_format': xunit_format,
                                              'launch_id': launch.id,
                                              'params': params})
            else:
                log.info('Connection to storage is not set in settings, '
                         'parse xml synchronously')
                parse_xml(xunit_format=xunit_format,
                          launch_id=launch.id,
                          params=params,
                          file_content=file_obj.read())
            return Response(status=status.HTTP_200_OK,
                            data={'launch_id': launch.id})
        return Response(status=status.HTTP_400_BAD_REQUEST)
