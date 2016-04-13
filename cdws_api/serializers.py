from django.utils import six

from common.models import Project, Settings

from testreport.models import TestPlan
from testreport.models import Launch
from testreport.models import Build
from testreport.models import TestResult
from testreport.models import LaunchItem
from testreport.models import Bug
from stages.models import Stage
from metrics.models import Metric, MetricValue

from authentication.serializers import AccountSerializer

from comments.models import Comment

from rest_framework import serializers

import logging


log = logging.getLogger(__name__)


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ('key', 'value')


class ProjectSerializer(serializers.ModelSerializer):
    settings = SettingsSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'settings')


class TestPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPlan


class TaskResultField(serializers.DictField):
    @staticmethod
    def child_to_representation(value):
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='replace')
        return value

    def to_representation(self, value):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return dict([
            (six.text_type(key), self.child_to_representation(val))
            for key, val in iter(value.items())
        ])


class AsyncResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    result = TaskResultField()
    status = serializers.CharField()

    def update(self, instance, validated_data):
        log.info("Update: {}".format(validated_data))

    def create(self, validated_data):
        log.info("Create: {}".format(validated_data))


class TasksResultField(serializers.DictField):
    def to_representation(self, value):
        output = {}
        for key, value in iter(value.items()):
            try:
                output[key] = LaunchItemSerializer(
                    LaunchItem.objects.get(pk=value)).data
            except LaunchItem.DoesNotExist:
                output[key] = LaunchItemSerializer(LaunchItem()).data
        return output


class BuildSerializer(serializers.ModelSerializer):
    last_commits = serializers.ReadOnlyField(source='get_last_commits')

    class Meta:
        model = Build
        fields = ('version', 'hash', 'branch', 'last_commits',
                  'commit_message', 'commit_author')


class LaunchSerializer(serializers.ModelSerializer):
    counts = serializers.ReadOnlyField()
    tasks = TasksResultField(source='get_tasks', read_only=True)
    parameters = serializers.ReadOnlyField(source='get_parameters')
    build = BuildSerializer(read_only=True)

    class Meta:
        model = Launch
        fields = ('id', 'test_plan', 'created', 'counts', 'tasks',
                  'state', 'started_by', 'created', 'finished', 'parameters',
                  'duration', 'build')


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult


class LaunchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaunchItem


class CommentSerializer(serializers.ModelSerializer):
    user_data = AccountSerializer(source='user', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'comment', 'submit_date', 'content_type', 'object_pk',
                  'user', 'user_data')


class BugSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Bug
        fields = ('id', 'externalId', 'name', 'status', 'regexp', 'updated')


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ('id', 'name', 'text', 'state',
                  'link', 'project', 'updated', 'weight')


class MetricSerializer(serializers.ModelSerializer):
    schedule = serializers.ReadOnlyField(source='get_schedule_as_cron')

    class Meta:
        model = Metric


class MetricValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricValue
