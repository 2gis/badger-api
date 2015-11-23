from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers

from cdws_api.views import ProjectViewSet
from cdws_api.views import TestPlanViewSet
from cdws_api.views import LaunchViewSet
from cdws_api.views import TestResultViewSet
from cdws_api.views import LaunchItemViewSet
from cdws_api.views import TaskResultViewSet
from cdws_api.views import CommentViewSet
from cdws_api.views import BugViewSet
from cdws_api.views import StageViewSet
from cdws_api.views import JenkinsViewSet
from cdws_api.views import RundeckViewSet
from cdws_api.views import MetricViewSet, MetricValueViewSet
from cdws_api.views import ReportFileViewSet

from authentication.views import LoginView
from authentication.views import LogoutView
from authentication.views import IsAuthorizedView
from authentication.views import UpdateSettingsView

from testreport.views import Base

router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'testplans', TestPlanViewSet)
router.register(r'launches', LaunchViewSet)
router.register(r'testresults', TestResultViewSet)
router.register(r'launch-items', LaunchItemViewSet)
router.register(r'tasks', TaskResultViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'bugs', BugViewSet)
router.register(r'stages', StageViewSet)
router.register(r'metrics', MetricViewSet)
router.register(r'metricvalues', MetricValueViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', Base.as_view(), name='dashboard'),
    url(r'^{0}/'.format(settings.CDWS_API_PATH), include(router.urls)),
    url(r'^{0}/auth/login'.format(settings.CDWS_API_PATH), LoginView.as_view(),
        name='api-auth-login'),
    url(r'^{0}/auth/logout'.format(settings.CDWS_API_PATH),
        LogoutView.as_view(), name='api-auth-logout'),
    url(r'^{0}/auth/get'.format(settings.CDWS_API_PATH),
        IsAuthorizedView.as_view(), name='api-auth-get'),
    url(r'^{0}/auth/update'.format(settings.CDWS_API_PATH),
        UpdateSettingsView.as_view(), name='api-auth-update'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^{0}/external/jenkins/(?P<project>[^/.]+)/'.
        format(settings.CDWS_API_PATH), JenkinsViewSet.as_view()),
    url(r'^{0}/external/rundeck/(?P<project>[^/.]+)/'.
        format(settings.CDWS_API_PATH), RundeckViewSet.as_view()),
    url(r'^{0}/external/report-xunit/(?P<testplan_id>[^/.]+)/'
        r'(?P<xunit_format>[^/.]+)/(?P<filename>[^/.]+)'.
        format(settings.CDWS_API_PATH), ReportFileViewSet.as_view()),
)

urlpatterns += staticfiles_urlpatterns()
