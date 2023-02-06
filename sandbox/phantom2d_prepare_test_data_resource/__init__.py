# coding=utf-8
import os.path
import logging

from sandbox import sdk2
from sandbox.common import patterns
from sandbox.projects.common import utils, binary_task
from sandbox.projects.metrika.utils.resource_types import Phantom2dDebugLogs, Phantom2dTestData
from sandbox.projects.metrika.utils import CommonParameters
from sandbox.projects.metrika.utils.base_metrika_task import with_parents, BaseMetrikaTask


@with_parents
class Phantom2dPrepareTestDataResource(BaseMetrikaTask):
    """
    Подготавливает ресурс с тестовыми данными для phantom2d.
    """

    class Parameters(CommonParameters):
        days_limit = sdk2.parameters.Integer("Количество дней с текущего дня для фильтрации",
                                             required=True,
                                             default=7,
                                             description="Будут отфильтрованы ресурсы, созданные раньше ограничения.")
        lines_limit = sdk2.parameters.Integer(
            "Количество строк, отфильтрованные из каждого ресурса по каждому отдельному хендлеру",
            default=1000,
        )

        _binary = binary_task.binary_release_parameters_list(stable=True)

    class Context(sdk2.Context):
        resource_id = None
        handlers = {}

    def on_execute(self):
        # must be synchronized with
        # https://a.yandex-team.ru/arc/trunk/arcadia/metrika/core/tests/metrika-core-beans/src/main/java/ru/yandex/autotests/metrika/core/beans/common/phantom2d/Handles.java#L5-17
        self.Context.handlers = {
            "/webvisor": 0,
            "/watch": 0,
            "/ping": 0,
            "/pixel": 0,
            "/pixeluser_storage_set": 0,
            "/informer": 0,
            "/clmap": 0,
            "/sync_cookie_decide": 0,
            "/sync_cookie_decidesync_cookie_decide_ok": 0,
            "/sync_cookie_image_start": 0,
            "/sync_cookie_image_check": 0,
            "/sync_cookie_image_decide": 0,
        }
        self._retrieve_artifacts()
        self._save_test_data()

    def _extract_test_data_from_resources(self, src, dst):
        logging.debug("Start extract from %s to %s", src, dst)
        count = 0
        with open(dst, 'w') as dst_h:
            with open(src) as src_h:
                for line in src_h:
                    try:
                        request = line.split()[1]
                    except IndexError:
                        logging.warning("Can not get request from line: %s", line)
                    else:
                        for handler in self.handlers:
                            if request.startswith(handler):
                                if self.handlers[handler] < self.Parameters.lines_limit:
                                    dst_h.write(line)
                                    count += 1
                                    self.handlers[handler] += 1
                                break

        logging.debug("Collected %d lines", count)

    def _save_test_data(self,):
        with sdk2.helpers.ProgressMeter("Saving resource"):
            resource = Phantom2dTestData(self, "Test data for phantom2d b2b tests", self.work_dir)
            logging.info("New phantom2d test data resource created with id - {0}".format(resource.id))
            self.Context.resource_id = resource.id

    def _retrieve_artifacts(self):
        from datetime import datetime, timedelta
        with sdk2.helpers.ProgressMeter("Retrieving artifacts"):
            for logs in sorted(list(Phantom2dDebugLogs.find(state='READY').limit(0)),
                               key=lambda x: x.created):
                if logs.created.date() > (datetime.now().date() - timedelta(days=self.Parameters.days_limit)):
                    logging.info("logs from {0}:{1}".format(logs.fqdn, logs.created))
                    cache_path_ro = str(sdk2.ResourceData(logs).path)
                    logs_path = os.path.join(self.work_dir, logs.fqdn)
                    self._extract_test_data_from_resources(cache_path_ro, logs_path)

    def on_release(self, parameters_):
        logging.debug("Release parameters: %r", parameters_)
        utils.set_resource_attributes(self.Context.resource_id, {"use": "stable", "ttl": "inf"})

    @patterns.singleton_property
    def work_dir(self):
        p = self.path("wd", "phantom2d_logs")
        p.mkdir(parents=True, exist_ok=True)
        return str(p)

    @property
    def handlers(self):
        return self.Context.handlers
