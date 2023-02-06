# -*- coding: utf-8 -*-

import time
import urllib2
import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.process import throw_subprocess_error
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.errors import SandboxTaskUnknownError


class BaseTesterTask(SandboxTask):
    """
    DEPRECATED-технология, надо использовать common.search.components
    Обращайтесь к mvel@, если что.
    """
    type = 'BASE_SEARCH_TASK'

    # start depends on resource type
    def _start_searcher(self, callbacks=None, **kvargs):
        raise SandboxTaskFailureError('Fuction "_start_searcher" doesn\'t exist for task')

    def _stop_searcher(self, subproc_list, session_id=None, **kvargs):
        for p in subproc_list:
            if p.poll() is None:
                try:
                    url = "http://127.0.0.1:{}/admin?action=shutdown".format(self._get_searcher_port())
                    logging.info("fetch url %s", url)
                    urllib2.urlopen(url, timeout=5).read()
                except Exception as e:
                    logging.error("Error in %s termination %s", p, e)
                    p.kill()
                    logging.info("%s - killed", p)

                for i in range(6):
                    if p.poll() is None:
                        logging.info("waiting 10sec for %s", p)
                        time.sleep(10)
                    else:
                        logging.info("%s - terminated", p)
                        break
                if p.poll() is None:
                    p.kill()
                    logging.info("%s - killed by timeout", p)
            else:
                logging.info("%s is finished with %s", p, p.returncode)

    def start_searchers_do_something_stop_searcher(self, callbacks, **kvargs):
        subproc_list = []
        try:
            # prepare and start searcher
            subproc_list = self._start_searcher(callbacks, **kvargs)

            callbacks.OnSearcherStarted(subproc_list)

        except:
            time.sleep(20)  # save coredump if died
            raise

        finally:
            for subproc in subproc_list:
                if subproc.poll() is not None:
                    throw_subprocess_error(subproc)

            self._stop_searcher(subproc_list, **kvargs)

    def _get_searcher_port(self):
        raise SandboxTaskUnknownError("No port.")
