from django.contrib import admin
from metrics.models import Metric, MetricValue


class MetricAdmin(admin.ModelAdmin):
    class Meta:
        model = Metric


class MetricValueAdmin(admin.ModelAdmin):
    class Meta:
        model = MetricValue


admin.site.register(Metric, MetricAdmin)
admin.site.register(MetricValue, MetricValueAdmin)
