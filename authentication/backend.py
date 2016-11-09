from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.backends import ModelBackend

import ldap3

import logging
log = logging.getLogger(__name__)


server = ldap3.Server(settings.AUTH_LDAP3_SERVER_URI)
connection = None


def get_connection(**kwargs):
    if 'dn' in kwargs and 'password' in kwargs:
        return ldap3.Connection(server, user=kwargs['dn'],
                                password=kwargs['password'], read_only=True)
    return ldap3.Connection(
        server,
        user=settings.AUTH_LDAP3_SEARCH_USER_DN,
        password=settings.AUTH_LDAP3_SEARCH_USER_PASSWORD,
        read_only=True)


def _get_dn_and_attributes_by_params(conn, params):
    if not conn.bind():
        log.error('Unable to bind with search user: {}'.format(
            conn.last_error))
        return None, None
    if not conn.search(**params):
        log.error('Search with params: {}, failed: {}'.format(params,
                                                              conn.result))
        return None, None
    log.debug('Search with base {search_base} '
              'and filter {search_filter} done'.format(**params))
    log.debug('Response is: {}'.format(conn.response))
    return conn.response[0]['dn'], conn.response[0]['attributes']


def create_or_update_user(params, username):
    try:
        user = User.objects.get(username__exact=username)
        for key, value in iter(params.items()):
            setattr(user, key, value)
    except ObjectDoesNotExist as e:
        log.debug(e)
        log.debug('Try to save user with params: {}'.format(params))
        user = User(**params)
    user.save()
    return user


class ADBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        if password == '':
            log.debug('Password is not set for authentication, return')
            return None
        log.debug('Authenticate username={username}, '
                  'password=***'.format(username=username))
        required_attributes = list(filter(
            lambda item: item is not None and item != '',
            settings.AUTH_LDAP3_ATTRIBUTES_MAPPING.values()))
        params = {
            'search_base': settings.AUTH_LDAP3_SEARCH_BASE,
            'search_filter': settings.AUTH_LDAP3_SEARCH_FILTER.format(
                username=username),
            'attributes': required_attributes
        }
        dn, attributes = _get_dn_and_attributes_by_params(get_connection(),
                                                          params)
        if dn is None:
            return None
        conn = get_connection(dn=dn, password=password)
        if not conn.bind():
            log.debug('Bind for dn: {} failed: {}'.format(dn,
                                                          conn.last_error))
            return None
        params = {}
        for key, value in iter(
                settings.AUTH_LDAP3_ATTRIBUTES_MAPPING.items()):
            if value is not None:
                if isinstance(attributes[value], list):
                    params[key] = attributes[value][0]
                else:
                    params[key] = attributes[value]
        return create_or_update_user(params, username)
