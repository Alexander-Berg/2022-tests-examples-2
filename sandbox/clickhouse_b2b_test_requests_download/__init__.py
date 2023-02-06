# coding=utf-8
import logging
import re
from datetime import datetime, timedelta

import six

from sandbox import sdk2
from sandbox.common import fs
from sandbox.projects.common import binary_task, decorators
from sandbox.projects.metrika import utils as metrika_utils
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_requests_download import handles
from sandbox.projects.metrika.utils import base_metrika_task, resource_types, settings
from sandbox.projects.metrika.utils.mixins import juggler_reporter
from sandbox.sdk2 import helpers, parameters, resource
from sandbox.projects.metrika.utils.parameters import hide

MAX_ITERATIONS = 20

QUERY_TEMPLATE = """
SELECT
    count() AS count, replaceRegexpAll(any(filtered_url), '{handle}(\\..+?)?\\?', '') as params
FROM (
    SELECT
        trim(TRAILING '&' FROM replaceRegexpAll(
            replaceRegexpAll(request, '({sub_params})=.*?(&|$)', ''),
                '([&?])(\\w+?=(&|$))+', '\\1'
            )
        ) as filtered_url
    FROM concatYtTablesRange('//logs/{table}/1d', '{StartDate}', '{FinishDate}')
    WHERE (path(request)='{handle}' or path(request) like '{handle}.%') AND status=200
)
GROUP BY cityHash64(arrayReduce('groupUniqArray', arraySort(extractURLParameters(assumeNotNull(filtered_url)))))
ORDER BY count DESC
"""

DTF = '%Y-%m-%d'
QUERY_TIMEOUT = 900
QUERY_TRIES = 5


class ClickHouseB2BTestsRequests(resource.AbstractResource):
    name = 'CLICKHOUSE_B2B_TESTS_REQUESTS'
    auto_backup = True


class ClickHouseB2BTestRequestsResource(resource_types.DefaultValueResourceMixin, parameters.Resource):
    resource_type = ClickHouseB2BTestsRequests.name
    owner = 'METRIKA'
    attrs = {'version': 'stable'}


@base_metrika_task.with_parents
class ClickHouseB2BTestRequestsDownload(base_metrika_task.BaseMetrikaTask, juggler_reporter.JugglerReporterMixin):
    name = 'CLICKHOUSE_B2B_TEST_REQUESTS_DOWNLOAD'

    DUP_RE = re.compile(r'(&|^)(\w+?=).*?&\2')

    @property
    def juggler_host(self):
        return self.type.name

    @property
    def juggler_service(self):
        return 'days-{}'.format(self.Parameters.data_window_size)

    class Parameters(metrika_utils.CommonParameters):
        kill_timeout = 5 * 60 * 60  # 16 hours

        data_window_size = parameters.Integer(
            'Период данных в днях', required=True, default=7,
            description='Количество дней за которые анализируются логи'
        )

        is_finish_date_relative = parameters.Bool('Конец периода относительно текущей даты', required=True, default=False)

        with is_finish_date_relative.value[True]:
            finish_date_relative = parameters.Integer('Сколько дней отступить в прошлое', required=True, default=1)

        with is_finish_date_relative.value[False]:
            finish_date_absolute = parameters.String('Конец периода в формате YYYY-MM-DD', required=True, default=(datetime.now() - timedelta(1)).strftime(DTF))

        with parameters.Group('Выходной ресурс') as output_resource_group:
            resource_ttl = parameters.String('TTL у ресурса, в днях', required=True, default=365)
            resource_attrs = parameters.Dict('Атрибуты ресурса', required=True, default={'version': 'stable'})

        limit = parameters.Integer('Максимальное количество запросов каждого вида', required=False)

        release_acceptance_only = parameters.Bool('Ручки только для приемки')

        with sdk2.parameters.Group('Секреты') as secrets_group:
            yt_token = sdk2.parameters.YavSecretWithKey('YT token', required=True, default='{}#yt-hahn-token'.format(settings.yav_uuid),
                                                        description="Секрет с токеном для доступа к YT")

        _binary = hide(binary_task.binary_release_parameters_list(stable=True))

    @decorators.memoized_property
    def _dates(self):
        if self.Parameters.is_finish_date_relative:
            finish_date = datetime.now() - timedelta(days=self.Parameters.finish_date_relative)
        else:
            finish_date = datetime.strptime(self.Parameters.finish_date_absolute, DTF)
        start_date = finish_date - timedelta(days=self.Parameters.data_window_size - 1)
        dates = {'StartDate': start_date.strftime(DTF), 'FinishDate': finish_date.strftime(DTF)}
        logging.info('Даты загрузки: {}'.format(dates))
        return dates

    @decorators.memoized_property
    def yt_client(self):
        from yt import wrapper
        return wrapper.YtClient(proxy='hahn', token=self.Parameters.yt_token.value())

    @decorators.retries(QUERY_TRIES)
    def execute_yt(self, query):
        from yt import clickhouse as chyt
        return list(chyt.execute(query, client=self.yt_client, alias='*ch_public', settings={'receive_timeout': QUERY_TIMEOUT}))

    def on_execute(self):
        for daemon, conf in handles.REQUESTS_CONF.iteritems():
            for handle_settings in conf['handles']:
                if self.Parameters.release_acceptance_only and not handle_settings['release_acceptance']:
                    continue

                handle = handle_settings['handle']
                with helpers.ProgressMeter('Processing {daemon} {handle}'.format(daemon=daemon, handle=handle)):
                    logging.info('==============> Start processing for {daemon} {handle}'.format(daemon=daemon, handle=handle))
                    query = QUERY_TEMPLATE.format(
                        handle=handle, sub_params='|'.join(handles.IRRELEVANT_PARAMS), table=conf['table'], **self._dates
                    )
                    if self.Parameters.limit:
                        query += 'LIMIT {}'.format(self.Parameters.limit)
                    logging.debug(query)

                    rows = self.execute_yt(query)
                    if rows:
                        destination_path = self.path('requests', daemon, *handle.strip('/').split('/'))
                        fs.make_folder(destination_path)
                        # тут пишем файлы по результатам запроса
                        # requests - 1 строка - 1 запрос без хоста и протокола, без sub_params, комбинации параметров не повторяются
                        # counters - 1 строка - число, сколько раз встретился этот запрос
                        # handle - 1 строка - ручка

                        total = self._process_rows(rows, destination_path)
                        (destination_path / 'total').write_text(six.text_type(total), encoding='utf8')
                        (destination_path / 'uniq').write_text(six.text_type(len(rows)), encoding='utf8')
                        (destination_path / 'handle').write_text(six.text_type(handle), encoding='utf8')
                        self.set_info('Для {daemon} {handle} обработано всего запросов {total}, уникальных {uniq}'.format(
                            daemon=daemon, handle=handle, total=total, uniq=len(rows)
                        ))
                    else:
                        logging.warning('No rows. Continue.')
                        self.set_info('Запросов не обнаружено для {daemon} {handle}'.format(daemon=daemon, handle=handle))

                    logging.info('==============> Finish processing for {daemon} {handle}'.format(daemon=daemon, handle=handle))

        with helpers.ProgressMeter('Preparing resource'):
            attrs = dict(self.Parameters.resource_attrs)
            attrs.update(**self._dates)
            attrs.update({ClickHouseB2BTestRequestsDownload.Parameters.data_window_size.name: self.Parameters.data_window_size})
            sdk2.ResourceData(ClickHouseB2BTestsRequests(
                self, '{StartDate} - {FinishDate}'.format(**self._dates),
                self.path('requests').as_posix(),
                ttl=self.Parameters.resource_ttl,
                **attrs
            )).ready()

    def _process_rows(self, rows, destination_path):
        total = 0
        with (destination_path / 'params').open('w', encoding='utf8') as params_file, (destination_path / 'counters').open('w', encoding='utf8') as counters_file:
            for row in rows:
                total += int(row['count'])
                counters_file.write(u'{}\n'.format(row['count']))
                params = self.DUP_RE.sub(r'\1\2', row['params']).encode('utf8')
                params_file.write(u'{}\n'.format(params))

        return total
