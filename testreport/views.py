from django.views.generic import TemplateView

import logging

log = logging.getLogger(__name__)


class Base(TemplateView):
    template_name = 'base.html'
