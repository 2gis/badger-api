import logging
log = logging.getLogger(__name__)


HANDLER_CHOICES = (
    ('count', 'Calculate count value'),
    ('cycletime', 'Calculate cycle time'),
    ('leadtime', 'Calculate lead time')
)


def count(data):
    return len(data)


def cycletime(data):
    if len(data) == 0:
        return 0

    avg_cycle_time = 0
    for issue in data:
        avg_cycle_time += issue.get_cycle_time().total_seconds()
    return int(avg_cycle_time / len(data))


def leadtime(data):
    if len(data) == 0:
        return 0

    avg_lead_time = 0
    for issue in data:
        avg_lead_time += issue.get_lead_time().total_seconds()

    return int(avg_lead_time / len(data))
