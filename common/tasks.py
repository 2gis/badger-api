from __future__ import absolute_import
from celery.exceptions import SoftTimeLimitExceeded

import celery
import subprocess

import logging
import datetime
import signal
import os

log = logging.getLogger(__name__)


@celery.task(time_limit=43200)
def launch_process(cmd, env={}):
    pid = None

    def sigterm_handler(signum, frame):
        log.debug('Get "{}", starting handler'.format(signum))
        if pid is None:
            log.warn("Pid is None, nothing to kill...")
            return
        log.debug('Killing process with id: {}...'.format(pid))
        os.kill(pid, signal.SIGTERM)

    signal.signal(signal.SIGTERM, sigterm_handler)

    start = datetime.datetime.now()
    cmd = cmd.replace('\n', ';').replace('\r', '')
    result = {
        'cmd': cmd,
        'env': env,
        'stdout': None,
        'stderr': None,
        'return_code': 0,
    }
    cwd = '/tmp/'
    if 'WORKSPACE' in env:
        cwd = env['WORKSPACE']
    try:
        cmd = subprocess.Popen(['bash', '-c', cmd], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env, cwd=cwd,
                               universal_newlines=False)
        pid = cmd.pid
        result['stdout'], result['stderr'] = cmd.communicate()
        result['return_code'] = cmd.returncode
    except subprocess.CalledProcessError as e:
        result['stdout'] = e.output
        result['return_code'] = e.returncode
    except OSError as e:
        result['stderr'] = e.strerror
        result['return_code'] = 127
    except SoftTimeLimitExceeded as e:
        result['stderr'] = 'Soft timeout limit exceeded. {}'.format(e)
        result['return_code'] = 1
    end = datetime.datetime.now()
    result['start'] = start.isoformat()
    result['end'] = end.isoformat()
    result['delta'] = (end - start).total_seconds()
    return result
