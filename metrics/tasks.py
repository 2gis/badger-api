from django.core.exceptions import ObjectDoesNotExist

from metrics.models import Metric, MetricValue
from metrics import handlers

from metrics.jira import request_jira_api

import celery
from datetime import timedelta

from django.conf import settings

import logging
log = logging.getLogger(__name__)


@celery.task()
def run_metric_calculation(metric_id):
    log.info('Getting metric {} from DB'.format(metric_id))
    try:
        metric = Metric.objects.get(pk=metric_id)
    except ObjectDoesNotExist:
        log.error('Metric with id {} was not found in DB'.format(metric_id))
        raise ObjectDoesNotExist

    expand = None
    fields = ['created', 'resolutiondate']
    if metric.handler in ['cycletime']:
        expand = ['changelog']

    method = getattr(handlers, metric.handler)
    if settings.JIRA_INTEGRATION:
        try:
            data = request_jira_api(metric.query, fields=fields, expand=expand)
        except Exception as e:
            metric.error = e
            metric.save()
            raise e

        log.info('Handling selected data started')
        try:
            value = method(data)  # handler value
            log.info('Handling selected data finished')
        except Exception as e:
            log.error('Selected data "{}" can not be handle by {}-handler: {}'.
                      format(data, metric.handler, e))
            metric.error = e
            metric.save()
            raise e

        metric.error = ''
        metric.save()
        log.info('Creating metric value for metric {}'.format(metric.name))
        MetricValue.objects.create(metric=metric, value=value)
        log.info('Metric created')
    else:
        log.info('Jira integration is off. '
                 'If you want to use this feature, turn it on.')


@celery.task()
def restore_metric_values(metric_id, query, step, handler, handler_field):
    expand = None
    if handler in ['cycletime', 'leadtime']:
        expand = ['changelog']

    if settings.JIRA_INTEGRATION:
        try:
            method = getattr(handlers, handler)
            data = request_jira_api(
                query=query,
                fields=['created', 'resolutiondate'],
                expand=expand)

            results = group_issues_by_step(data, int(step), handler_field)

        except Exception as e:
            raise e

        for date, group in results.items():
            log.info('Handling selected data started')
            try:
                value = method(group)  # handler value
                log.info('Handling selected data finished')
            except Exception as e:
                log.error(
                    'Selected data "{}" can not be handle by {}-handler: {}'.
                    format(data, handler, e))
                raise e
            MetricValue.objects.create(metric_id=metric_id, value=value,
                                       created=date)
    else:
        log.info('Jira integration is off. '
                 'If you want to use this feature, turn it on.')


def group_issues_by_step(issues, step_in_days, field):
    sorted_issues = sorted(
        issues, key=lambda item: item.get_datetime(field))

    start_date = sorted_issues[-1].get_datetime(field)
    current_interval = start_date - timedelta(days=step_in_days)

    group_issues = {}
    tmp = []
    while len(sorted_issues) != 0:
        issue = sorted_issues.pop()
        if issue.get_datetime(field) >= current_interval:
            tmp.append(issue)
        else:
            group_issues[(current_interval + timedelta(days=step_in_days))
                         .strftime('%Y-%m-%d')] = tmp
            current_interval = current_interval - timedelta(days=step_in_days)
            sorted_issues.append(issue)
            tmp = []

    if len(tmp) != 0:
        group_issues[(current_interval + timedelta(days=step_in_days))
                     .strftime('%Y-%m-%d')] = tmp

    return group_issues
