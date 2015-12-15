import logging

from django.contrib import admin

from common.models import Project
from common.models import Settings

from testreport.models import Launch
from testreport.models import TestPlan
from testreport.models import TestResult
from testreport.models import LaunchItem
from testreport.models import Bug

log = logging.getLogger(__name__)

admin.site.disable_action('delete_selected')


class ProjectAdmin(admin.ModelAdmin):
    actions = ['delete_selected']


def force_delete(modeladmin, request, queryset):
    try:
        queryset.delete()
    except Exception as e:
        log.error(e)

force_delete.short_description = 'Delete selected items w/o confirmation'


class LaunchAdmin(admin.ModelAdmin):
    actions = [force_delete]


class LaunchItemInline(admin.StackedInline):
    actions = ['delete_selected']
    model = LaunchItem
    extra = 0


class TestPlanAdmin(admin.ModelAdmin):
    inlines = [LaunchItemInline]
    actions = [force_delete]


class TestResultAdmin(admin.ModelAdmin):
    actions = ['delete_selected']


class LaunchItemAdmin(admin.ModelAdmin):
    actions = ['delete_selected']


class BugAdmin(admin.ModelAdmin):
    actions = ['delete_selected']


admin.site.register(LaunchItem, LaunchItemAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Settings, ProjectAdmin)
admin.site.register(Launch, LaunchAdmin)
admin.site.register(TestPlan, TestPlanAdmin)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(Bug, BugAdmin)
