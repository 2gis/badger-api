from django.contrib import admin
from stages.models import Stage


class StageAdmin(admin.ModelAdmin):
    fields = ('name', 'project', 'text', 'link', 'state', 'updated', 'weight')

    class Meta:
        model = Stage


admin.site.register(Stage, StageAdmin)
