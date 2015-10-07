import requests
import json
import logging

from django.conf import settings

from rest_framework.exceptions import APIException

from datetime import datetime, timedelta

log = logging.getLogger(__name__)


def request_jira_api(query, fields=None, max_results=500, expand=None):
    url = 'https://{}{}'.format(
        settings.BUG_TRACKING_SYSTEM_HOST,
        settings.TRACKING_SYSTEM_SEARCH_PATH)
    data = json.dumps({'jql': query,
                       'maxResults': max_results,
                       'fields': fields,
                       'expand': expand})
    auth = (settings.BUG_TRACKING_SYSTEM_LOGIN,
            settings.BUG_TRACKING_SYSTEM_PASSWORD)
    headers = {'Content-Type': 'application/json'}

    response = None

    try:
        log.info('url="{}", data="{}", headers="{}"'.
                 format(url, data, headers))
        response = requests.post(url=url, data=data,
                                 auth=auth, headers=headers)
        result = response.json()
    except Exception as e:
        log.error('Some problems appeared during connection to "{}", '
                  'auth="{}", data="{}", headers="{}", response="{}"'.
                  format(url, auth, data, headers, response))
        raise e

    log.debug(result)
    errors = []
    if 'errors' in result:
        errors += result['errors']
    if 'errorMessages' in result:
        errors += result['errorMessages']
    if len(errors) != 0:
        log.debug(errors)
        raise APIException(
            "Tracking system: '{}'".format('\n'.join(errors)))
    return build_objects(result)


def build_objects(issues_dict):
    if 'issues' in issues_dict:
        issues_dict = issues_dict['issues']
    output = []
    for issue in issues_dict:
        output.append(JiraIssue(issue))
    return output


class JiraIssue(object):
    source = None

    def __init__(self, issue):
        self.source = issue

    def _string_to_date(self, string_date):
        return datetime.strptime(string_date[:19], '%Y-%m-%dT%H:%M:%S')

    def _get_timedelta(self, start_date, end_date, exclude_weekend=False):
        if exclude_weekend:
            weekends = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() in [5, 6]:
                    weekends += 1
                current_date += timedelta(days=1)
            return end_date - start_date - timedelta(days=weekends)

        return end_date - start_date

    def get_datetime(self, field):
        if field == 'finish_date':
            return self._get_finish_date()
        elif field == 'created':
            return self._get_create_date()
        elif field == 'resolutiondate':
            return self._get_resolution_date()
        else:
            raise RuntimeError(
                'Unable to get date field with name {}'.format(field))

    def _get_create_date(self):
        return datetime.strptime(
            self.source['fields']['created'][:10], '%Y-%m-%d')

    def _get_resolution_date(self):
        return datetime.strptime(
            self.source['fields']['resolutiondate'][:10], '%Y-%m-%d')

    def _get_finish_date(self):
        return self.handle_changelog('finish_date')

    def get_cycle_time(self):
        return self._get_timedelta(
            self.handle_changelog('cycletime_start_date'),
            self._get_finish_date(),
            exclude_weekend=True)

    def get_lead_time(self):
        return self._get_timedelta(
            self._string_to_date(self.source['fields']['created']),
            self._get_finish_date(),
            exclude_weekend=True)

    def handle_changelog(self, type):
        for history in self.source['changelog']['histories']:
            for item in history['items']:
                if item['field'] == 'status':
                    finish_date = self._string_to_date(history['created'])
                    if item['fromString'] == 'Взят в бэклог':
                        cycletime_start_date = \
                            self._string_to_date(history['created'])
                    if item['toString'] == 'Open':
                        cycletime_start_date = \
                            self._string_to_date(history['created'])

        if type == 'finish_date':
            return finish_date
        if type == 'cycletime_start_date':
            return cycletime_start_date
