# coding=utf-8

import time
import logging

import yaml

from sandbox.projects.metrika.utils import parameters
import sandbox.sdk2 as sdk2
import sandbox.common.types.task as ctt
import sandbox.projects.common.binary_task as binary_task

import sandbox.projects.metrika.utils.resource_types as rt
import sandbox.projects.metrika.utils.settings as settings
import sandbox.projects.metrika.utils.pipeline.pipeline_errors as pipeline_errors
import sandbox.projects.metrika.utils.pipeline.pipeline as pipeline
import sandbox.projects.metrika.utils.base_metrika_task as base_metrika_task
from sandbox.projects.metrika.core.metrika_core_phantom2d_load_test_stand_create import MetrikaCorePhantom2dLoadTestStandCreate
from sandbox.projects.metrika.admins.metrika_yandex_tank_stand_create import MetrikaYandexTankStandCreate

from sandbox.projects.metrika.utils import render
from sandbox.projects.metrika.utils import CommonParameters


PROGRAMS = [
    'phantom2d',
]


@base_metrika_task.with_parents
class MetrikaLoadTesting(pipeline.PipelineBaseTask):
    class Parameters(CommonParameters):
        with sdk2.parameters.Group('Общие параметры') as common_parameters:
            with sdk2.parameters.RadioGroup('Датацентр') as datacenter:
                datacenter.values['vla'] = datacenter.Value(default=True)
                datacenter.values['sas'] = None
                datacenter.values['iva'] = None

            pipeline_fails_if_load_test_fails = sdk2.parameters.Bool(
                'Завершать конвейер с ошибкой при ошибках в результате нагрузчного тестирования',
                default=True,
            )

        with sdk2.parameters.Group('Настройки стенда') as stand_settings:
            use_custom_stand = sdk2.parameters.Bool(
                'Я хочу указать, какой стенд использовать',
                default=False,
                description='мишень для танка'
            )

            with use_custom_stand.value[False]:
                program = sdk2.parameters.String(
                    'Программа',
                    required=True,
                    choices=parameters.choices(
                        PROGRAMS,
                        autocomplete=True,
                    )
                )
                with program.value['phantom2d']:
                    phantom2d_version = sdk2.parameters.String(
                        'phantom2d version',
                        required=True,
                    )

                do_not_delete_stand = sdk2.parameters.Bool(
                    'Не удалять сденд после стрельбы',
                    default=False,
                )

            with use_custom_stand.value[True]:
                custom_stand_host = sdk2.parameters.String(
                    'Хост произвольного стенда',
                    required=True,
                )
                custom_stand_port = sdk2.parameters.Integer(
                    'Порт произвольного стенда',
                    required=True,
                    default=None,
                )

        with sdk2.parameters.Group('Настройки танка') as tank_settings:
            use_custom_tank = sdk2.parameters.Bool(
                'Я хочу указать, какой танк использовать',
                default=False,
            )
            with use_custom_tank.value[False]:
                do_not_delete_tank = sdk2.parameters.Bool(
                    'Не удалять танк после стрельбы',
                    default=False,
                )

            with use_custom_tank.value[True]:
                custom_tank_host = sdk2.parameters.String(
                    'Хост произвольного танка',
                    required=True,
                )
                custom_tank_port = sdk2.parameters.Integer(
                    'Порт произвольного танка',
                    required=True,
                    default=None,
                )

        with sdk2.parameters.Group('Настройки стрельбы') as load_profile:
            use_custom_tank_config = sdk2.parameters.Bool(
                'Я хочу использовать свой конфиг для танка',
                default=False,
                description='JSON. phantom["address"] будет заменён на адрес стенда.',
            )
            load_test_description = sdk2.parameters.String(
                'Описание для стрельбы в lunapark',
                default='',
            )
            load_test_label = sdk2.parameters.String(
                'Дополнительная метка для стрельбы в lunapark',
                default='',
            )
            load_test_component = sdk2.parameters.String(
                'Компонент стрельбы в lunapark',
                default='',
                description='Используется в регрессии'
            )
            with use_custom_tank_config.value[False]:
                tracker_issue = sdk2.parameters.String(
                    'Тикет (startrek)',
                    required=True,
                )
                schedule = sdk2.parameters.String(
                    'Расписание (schedule)',
                    default='line(1, 1000, 1m)',
                )
                ammofile = sdk2.parameters.Resource(
                    'Ресурс с патронами',
                )
            with use_custom_tank_config.value[True]:
                custom_tank_config = sdk2.parameters.JSON(
                    'Конфиг танка',
                    required=True,
                    default=None,
                    description='json',
                )

        with sdk2.parameters.Group('Secrets parameters') as secrets_parameters:
            deploy_token_yav_secret = sdk2.parameters.YavSecret(
                'YP access secret',
                required=True,
                default=settings.yav_uuid,
                description='Used in requests to yp api',
            )
            deploy_token_yav_secret_key = sdk2.parameters.String(
                'YP access secret key',
                required=True,
                default='deploy-token',
            )

        _binary = binary_task.binary_release_parameters_list(stable=True)

    class Context(pipeline.PipelineBaseTask.Context):
        stand_host = None
        stand_port = None
        tank_host = None
        tank_port = None
        tank_config = None
        tank_load_test_id = None
        subtasks = []
        subtasks_index = {}
        lunapark_url = None
        lunapark_id = None
        load_test_result = True
        load_test_error = None

    @property
    def tank(self):
        import sandbox.projects.metrika.admins.metrika_load_testing.tank as tank

        if not self.Context.tank_host or not self.Context.tank_port:
            raise ValueError("Context tank_host or tank_port are not set")

        return tank.Tank(
            self.Context.tank_host,
            self.Context.tank_port,
        )

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client

        secret = self.Parameters.deploy_token_yav_secret.data()
        token = secret[self.Parameters.deploy_token_yav_secret_key]

        return metrika.pylib.deploy.client.DeployAPI(token=token)

    @property
    def tank_stage_id(self):
        return 'mlt-tank-{}'.format(self.id)

    @property
    def stand_stage_id(self):
        return 'mlt-{}-{}'.format(
            self.Parameters.program,
            self.id,
        )

    def create_stages(self):
        """
        Order of steps are important.
        """
        steps = [
            (self.step_prepare_stands, 'Подготовка стендов'),
            (self.step_run_load_test, 'Запуск стрельбы'),
            (self.step_await_load_test, 'Ожидание результатов стрельбы'),
            (self.step_analyze_load_test_results, 'Анализ результатов стрельбы'),
        ]
        if not self.Parameters.do_not_delete_tank and not self.Parameters.use_custom_tank:
            steps.append((self.step_cleanup_tank, 'Удаление стенда с танком'))
        if not self.Parameters.do_not_delete_stand and not self.Parameters.use_custom_stand:
            steps.append((self.step_cleanup_stand, 'Удаление стенда с программой'))

        steps.append((self.step_finalize, 'Завершение'))
        return steps

    def step_prepare_stands(self):
        subtasks_to_run = []
        i = 0

        if not self.Parameters.use_custom_stand:
            params = {
                'stage_id': self.stand_stage_id,
                'stage_dc': self.Parameters.datacenter,
                'phantom2d_version': self.Parameters.phantom2d_version,
            }
            subtasks_to_run.append((MetrikaCorePhantom2dLoadTestStandCreate, params))
            self.Context.subtasks_index['stand'] = i
            i += 1
        else:
            self.Context.stand_host = self.Parameters.custom_stand_host
            self.Context.stand_port = self.Parameters.custom_stand_port

        if not self.Parameters.use_custom_tank:
            params = {
                'stage_id': self.tank_stage_id,
                'stage_dc': self.Parameters.datacenter,
            }
            subtasks_to_run.append((MetrikaYandexTankStandCreate, params))
            self.Context.subtasks_index['tank'] = i
        else:
            self.Context.tank_host = self.Parameters.custom_tank_host
            self.Context.tank_port = self.Parameters.custom_tank_port

        if subtasks_to_run:
            self.run_subtasks(subtasks_to_run, subtasks_variable=self.Context.subtasks)

        if self.Context.subtasks:
            stand_task_index = self.Context.subtasks_index.get('stand')
            if stand_task_index is not None:
                stand_task_id = self.Context.subtasks[stand_task_index]
                stand_task = sdk2.Task[stand_task_id]
                self.Context.stand_host = stand_task.Parameters.output_host
                self.Context.stand_port = stand_task.Parameters.output_port

            tank_task_index = self.Context.subtasks_index.get('tank')
            if tank_task_index is not None:
                tank_task_id = self.Context.subtasks[tank_task_index]
                tank_task = sdk2.Task[tank_task_id]
                self.Context.tank_host = tank_task.Parameters.output_host
                self.Context.tank_port = tank_task.Parameters.output_port

    def step_run_load_test(self):
        with self.memoize_stage.run_load_test(commit_on_entrance=False):
            logging.info('Step run load test')
            config = self.get_tank_config()
            self.Context.tank_load_test_id = self.tank.start_load_test(config)

    def step_await_load_test(self):
        with self.memoize_stage.await_load_test(commit_on_entrance=False):
            logging.info('Step await load test started')
            tank = self.tank

            while True:
                is_finished, status = tank.is_load_test_finished(self.Context.tank_load_test_id)
                if not is_finished:
                    logging.info('Load test in progress: %s' % status)
                    time.sleep(15)
                else:
                    if not status.get('lunapark_url'):
                        message = 'Load test is finished, but lunapark_url was not found: %s' % status
                        raise pipeline_errors.PipelineAbortError(message)

                    if not status.get('lunapark_id'):
                        message = 'Load test is finished, but lunapark_id was not found: %s' % status
                        raise pipeline_errors.PipelineAbortError(message)

                    self.Context.lunapark_url = status['lunapark_url']
                    self.Context.lunapark_id = status['lunapark_id']

                    logging.info('Load test complete: %s' % status)
                    break

    def step_analyze_load_test_results(self):
        import metrika.pylib.http as http

        with self.memoize_stage.analyze_load_test_results(commit_on_entrance=False):
            url = 'https://lunapark.yandex-team.ru/api/job/{}/sla.json'.format(
                self.Context.lunapark_id,
            )
            data = http.request(url).json()[0]
            if not data['resolution']:
                self.Context.load_test_result = False
                self.Context.load_test_error = data['failed_kpis']

    def step_cleanup_tank(self):
        with self.memoize_stage.cleanup_tank(commit_on_entrance=False):
            logging.info('Step cleanup tank started')
            self.deploy_client.stage.remove_stage(self.tank_stage_id)

    def step_cleanup_stand(self):
        with self.memoize_stage.cleanup_stand(commit_on_entrance=False):
            logging.info('Step cleanup stand started')
            self.deploy_client.stage.remove_stage(self.stand_stage_id)

    def step_finalize(self):
        info = render(
            'resources/task_info.j2',
            context={
                'use_custom_stand': self.Parameters.use_custom_stand,
                'use_custom_tank': self.Parameters.use_custom_tank,
                'do_not_delete_stand': self.Parameters.do_not_delete_stand,
                'do_not_delete_tank': self.Parameters.do_not_delete_tank,
                'stand_host': self.Context.stand_host,
                'stand_port': self.Context.stand_port,
                'tank_host': self.Context.tank_host,
                'tank_port': self.Context.tank_port,
                'lunapark_url': self.Context.lunapark_url,
                'load_test_result': self.Context.load_test_result,
                'load_test_error': self.Context.load_test_error,
                'stand_stage_id': self.stand_stage_id,
                'tank_stage_id': self.tank_stage_id,
            },
        )
        info = info.strip()
        self.set_info(info, do_escape=False)

        if not self.Context.load_test_result and 'ANALYZE_OK' not in self.Parameters.tags:
            message = 'found errors in load test result: {}'.format(self.Context.load_test_error)
            if self.Parameters.pipeline_fails_if_load_test_fails:
                raise pipeline_errors.PipelineError(message)

    def is_all_tests_passed(self):
        return self.Context.load_test_result

    def get_stand_address(self):
        if not self.Context.stand_host or not self.Context.stand_port:
            raise ValueError("Context stand_host or stand_port are not set")

        return '%s:%s' % (self.Context.stand_host, self.Context.stand_port)

    def get_tank_config(self):
        if self.Parameters.use_custom_tank_config:
            config = self.Parameters.custom_tank_config
            config['phantom']['address'] = self.get_stand_address()
            if config.get('uploader'):
                job_name = config['uploader'].get('job_name')
                if job_name:
                    job_name = '%s[%s]' % (job_name, self.Parameters.load_test_label)
                else:
                    job_name = self.Parameters.load_test_label
                if job_name:
                    config['uploader']['job_name'] = job_name

                if self.Parameters.load_test_description:
                    config['uploader']['job_dsc'] = self.Parameters.load_test_description
                if self.Parameters.load_test_component:
                    config['uploader']['component'] = self.Parameters.load_test_component
        else:
            config = self.build_tank_config()

        yaml_config = yaml.dump(config)
        self.Context.tank_config = yaml_config
        return yaml_config

    def get_program_name(self):
        if self.Parameters.use_custom_stand:
            program = 'custom'
        else:
            program = self.Parameters.program
        return program

    def get_load_test_label(self):
        label = '[metrika-load-testing][%s]' % self.get_program_name()
        if self.Parameters.load_test_label:
            label = '%s[%s]' % (label, self.Parameters.load_test_label)
        return label

    def build_tank_config(self):
        config = {
            'phantom': {
                'address': self.get_stand_address(),
                'instances': 30000,
                'ammofile': self.get_ammofile_url(),
                'load_profile': {
                    'load_type': 'rps',
                    'schedule': self.Parameters.schedule,
                },
                'connection_test': False,
            },
            'uploader': {
                'enabled': True,
                'api_address': 'https://lunapark.yandex-team.ru/',
                'job_name': self.get_load_test_label(),
                'job_dsc': self.Parameters.load_test_description,
                'operator': self.author,
                'task': self.Parameters.tracker_issue,
            },
            'telegraf': {
                'enabled': False,  # disables target monitoring via ssh
            },
            'neuploader': {
                'enabled': False,  # disables upload to luna.yandex-team.ru
            }
        }
        if self.Parameters.load_test_component:
            config['uploader']['component'] = self.Parameters.load_test_component
        return config

    def get_ammofile_url(self):
        if self.Parameters.ammofile:
            return self.Parameters.ammofile.http_proxy
        else:
            ammofile_resource = sdk2.Resource.find(
                type=rt.MetrikaLoadTestingAmmofile,
                attrs={
                    'released': ctt.ReleaseStatus.STABLE,
                    'program': self.Parameters.program,
                },
                limit=1,
            )
            return ammofile_resource.first().http_proxy
