from sandbox import sdk2
from sandbox.common.types import task as ctt
import sandbox.common.types.misc as ctm
from sandbox.projects.common.arcadia import sdk
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.process import run_process
from sandbox.projects import resource_types

import sandbox.projects.common.constants as consts
import logging
import os
import datetime

WAIT_TIMEOUT = 5 * 3600
YQL_TOKEN_OWNER = 'USERSESSIONSTOOLS'
YQL_TOKEN_NAME = 'SCARAB_YQL_TOKEN'

SUPERAPP_TABLE_SUFFIX = 'superapp-metrika-mobile-log'
DEFAULT_TABLE_SUFFIX = 'appmetrica-yandex-events'


class CreateAndTestMobileUserSession(sdk2.Task):
    class Parameters(sdk2.Parameters):
        deviceID = sdk2.parameters.String(
            'device_id',
            description='Device ID',
            multiline=False,
            required=False
        )

        UUID = sdk2.parameters.String(
            'uuid',
            description='UUID',
            multiline=False,
            required=False
        )

        apiKey = sdk2.parameters.String(
            'api_key',
            description='Api key of app in Metrica',
            multiline=False,
            required=True
        )

        eventsDate = sdk2.parameters.String(
            'events_date',
            description='Date when events produced. Format: YYYY-MM-DD',
            multiline=False,
            required=True
        )

        events_start_time = sdk2.parameters.String(
            'events_start_time',
            description='Time when events start produced. Format: HH:MM',
            multiline=False,
            required=False
        )

        events_end_time = sdk2.parameters.String(
            'events_end_time',
            description='Time when events stop produced. Format: HH:MM',
            multiline=False,
            required=False
        )
        use_trunk_scarab = sdk2.parameters.Bool(
            "Use scarab from trunk",
            default_value=False,
        )

        arcadiaUrl = sdk2.parameters.ArcadiaUrl()

    class Context(sdk2.Context):
        YQL_executor_task_id = None
        ReportLogsTester_id = None

    class Requirements(sdk2.Task.Requirements):
        environments = (environments.PipEnvironment('pyscarab'),
                        environments.PipEnvironment('yandex-yt', version='0.10.8'),
                        environments.PipEnvironment('scarab'),
                        environments.PipEnvironment('yandex-yt-yson-bindings-skynet', version="0.3.32-0"),
                        environments.PipEnvironment('yql', version="1.2.101"),)
    def convert_scarab_to_ksv(self, input_file, output_file):
        with open (output_file, "a") as events_out:
            with open (input_file, "r") as events:
                for line in events:
                    events_out.write("\t\t{}".format(line))


    def on_execute(self):
        if (self.Context.restart == ctm.NotExists):
            logging.info('CreateTestUserSessionTask: Run yql')
            yql_table = '`tmp/bagiro44/create-scarab-session-test/in/' + str(self.Parameters.deviceID) + '-' + str(self.id) + '`'
            input_table = '//tmp/bagiro44/create-scarab-session-test/in/' + str(self.Parameters.deviceID) + '-' + str(self.id)
            output_table = '//tmp/bagiro44/create-scarab-session-test/out/' + self.Parameters.deviceID + '-' + str(self.id)

            token = sdk2.Vault.data(YQL_TOKEN_OWNER, YQL_TOKEN_NAME)
            os.environ["YT_TOKEN"] = token
            query = self._build_query(yql_table, token)
            logging.info('CreateTestUserSessionTask: yql query is - ' + query + '')
            self.run_yql_query(query, 'hahn', token)

            arcadia_url = self.Parameters.arcadiaUrl
            task_dir = str(self.path('python_converter'))
            target = 'quality/logs/scarab/logsng2scarab'
            logging.info('CreateTestUserSessionTask: clone and build logsng2scarab ')
            self.clone_and_buld(arcadia_url, target)

            work_dir = task_dir + '/' + target
            run_process([str(work_dir)+'/logsng2scarab', '-s', 'hahn.yt.yandex.net', '-op', 'convert_mobile_app_log', '-i', input_table, '-d', self.Parameters.eventsDate, '-o', output_table], work_dir=work_dir, shell=True, timeout=10000, log_prefix='run_converter', outputs_to_one_file=True)

            prepared_events = str(self.path('result.txt'))
            ksv_prepared_events = str(self.path('ksv_result.txt'))
            self.read_table(token, 'hahn', output_table, prepared_events)
            self.convert_scarab_to_ksv(prepared_events, ksv_prepared_events)
            if os.stat(prepared_events).st_size == 0:
                raise Exception("!!!No events for DeviceID - " + str(self.Parameters.deviceID))

            self.event_resource = resource_types.PLAIN_TEXT(self, 'Events prepared fot US', ksv_prepared_events)
            self.events = sdk2.ResourceData(resource_types.PLAIN_TEXT(self, 'Events prepared fot US', ksv_prepared_events))
            self.events.ready()
            self.Context.restart = "false"

            subtask_id = self.create_user_session_test_subtask()
            self.Context.subtask_id = subtask_id

            logging.info('CreateTestUserSessionTask: Subtask ID is ' + str(subtask_id))

        if (self.Context.ReportLogsTester_id != ctm.NotExists):
            subtask_status = self.server.task[self.Context.ReportLogsTester_id].read()["status"]
            logging.info('CreateTestUserSessionTask: Subtask status is - ' + str(subtask_status))
            if (subtask_status not in (ctt.Status.SUCCESS, )):
                raise Exception("User session subtask is failed")

        logging.info('CreateTestUserSessionTask: Finish task')

    def _build_query(self, output_path, token):
        where_params = []
        if self.Parameters.deviceID != '':
            where_params.append('DeviceID  == "' + self.Parameters.deviceID + '"')
        if self.Parameters.UUID != '':
            where_params.append('`UUID` == "' + self.Parameters.UUID + '"')
        if len(where_params) == 0:
            raise Exception("NEED TO SET UUID OR DEVICEID")
        if self.Parameters.apiKey != '':
            where_params.append('APIKey == ' + self.Parameters.apiKey)
        where_part = 'WHERE ' + ' AND '.join(where_params)
        query = ('USE hahn;\n'
                'insert into ' + output_path + '\n'
                'SELECT *\n'
                'FROM  ' + self.resolve_input_metrica_tables(token, False) + '\n'
                '' + where_part + '\n'
                'UNION ALL \n'
                'SELECT *\n'
                'FROM ' + self.resolve_input_metrica_tables(token, True) + '\n'
                '' + where_part + '\n')
        return query

    def day_input_tables(self, default_table):
        table_name = DEFAULT_TABLE_SUFFIX if default_table else SUPERAPP_TABLE_SUFFIX
        return '`logs/' + table_name + '/1d/' + self.Parameters.eventsDate + '`'

    def five_min_input_tables(self, default_table):
        table_name = DEFAULT_TABLE_SUFFIX if default_table else SUPERAPP_TABLE_SUFFIX
        if self.Parameters.events_start_time and self.Parameters.events_end_time:
            h_s = self.Parameters.events_start_time.split(':')[0]
            h_f = self.Parameters.events_end_time.split(':')[0]
            m_s = str((int(self.Parameters.events_start_time.split(':')[1]) / 5) * 5)
            m_f = str((int(self.Parameters.events_end_time.split(':')[1]) / 5) * 5)
            start_time = '{}:{}'.format(h_s if len(h_s) == 2 else '0' + h_s, m_s if len(m_s) == 2 else '0' + m_s)
            finish_time = '{}:{}'.format(h_f if len(h_f) == 2 else '0' + h_f, m_f if len(m_f) == 2 else '0' + m_f)
            return 'RANGE(`logs/' + table_name + '/stream/5min`,`' + self.Parameters.eventsDate + 'T' + start_time + ':00`,`' + self.Parameters.eventsDate + 'T' + finish_time + ':00`)'
        return 'RANGE(`logs/' + table_name + '/stream/5min`,`' + self.Parameters.eventsDate + 'T00:00:00`,`' + self.Parameters.eventsDate + 'T23:55:00`)'

    def check_exist_table(self, table, token):
        import yt.wrapper as yt
        yt.config.set_proxy("hahn")
        return yt.exists('//logs/superapp-metrika-mobile-log/1d/' + self.Parameters.eventsDate)

    def resolve_input_metrica_tables(self, token, default_table):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        if self.Parameters.eventsDate == now:
            return self.five_min_input_tables(default_table)
        else:
            day_tables = self.day_input_tables(default_table)
            if self.check_exist_table(day_tables, token):
                return day_tables
            else:
                return self.five_min_input_tables(default_table)

    def run_yql_query(self, query, server, token):
        from yql.api.v1.client import YqlClient
        yql_client = YqlClient(db=server, token=token)
        logging.info('Make query:\n%s', query)
        request = yql_client.query(query, syntax_version=1)
        request.encoding = 'utf-8'
        request.run()

        if not request.get_results().is_success:
            error_description = '\n'.join([str(err) for err in request.get_results().errors])
            logging.error(error_description)
            raise RuntimeError(error_description)

        return request.get_results().table

    def clone_and_buld(self, arcadia_url, api):
        arcadia_dir = sdk.do_clone(arcadia_url, self)
        sdk.do_build(
             build_system=consts.YMAKE_BUILD_SYSTEM,
             source_root=arcadia_dir,
             targets=[api],
             build_type=consts.RELEASE_BUILD_TYPE,
             results_dir=str(self.path('python_converter')),
             clear_build=False,
             use_dev_version=False,
             sanitize=False,
             checkout=True,
         )

    def yt_read_table(self, token, claster, table):
        from yt.wrapper import YtClient
        client = YtClient(claster, token)
        return client.read_table(table, format='json', raw=False)

    def read_table(self, token, claster, table, file):
        file = open(file, "w+")
        t = self.yt_read_table(token, claster, table)
        for item in t:
            file.write(item['value']+'\n')
        file.close()

    @property
    def _notifications(self):
        return self.server.task[self.id].read()["notifications"]

    def _create_sdk1_subtask(self, task_type, description, parameters):
        task = self.server.task({
            'type': task_type,
            'context': parameters,
            'children': True,
         })

        update = {
             'description': description,
             'notifications': self._notifications,
             'owner': self.owner,
             'priority': {
                 'class': self.Parameters.priority.cls,
                 'subclass': self.Parameters.priority.cls,
             },
         }

        task_id = task['id']
        self.server.task[task_id].update(update)
        self.server.batch.tasks.start.update([task_id])

        return task_id

    def create_user_session_test_subtask(self):
        parameters = {
            'log_name': 'scarab_log',
            'input_data': self.event_resource.id,
            'checkout_arcadia_from_url': self.Parameters.arcadiaUrl,
            'make_bin_by_ya_make': self.Parameters.use_trunk_scarab,
            'log_by_columns' : False,
            'make_bin_by_ya_make' : True
        }

        logging.info('ReportLogsTester task parameters: {}'.format(parameters))

        subtask = self._create_sdk1_subtask(
            task_type='TEST_REPORT_LOGS',
            description='Check mobile scarab events',
            parameters=parameters,
        )

        logging.debug('ReportLogsTester task id: {}'.format(subtask))

        self.Context.ReportLogsTester_id = subtask

        raise sdk2.WaitTask(
            subtask,
            ctt.Status.Group.FINISH | ctt.Status.Group.BREAK,
            timeout=max(self.Parameters.kill_timeout, WAIT_TIMEOUT),
            wait_all=True,
        )
