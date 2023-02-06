import os
import yaml

from dmp_suite import datetime_utils as dtu
from dmp_suite.decorators import try_except, compose, measure_time
from dmp_suite.exceptions import DWHError
from dmp_suite.ssas import OlapCube
from dmp_suite.ssas.ssas import ProcessTypes, ScriptTypes, OlapCubeType, \
    SSASTemplate, ServerTypes

CONFIG_FILE_NAME = 'config.yaml'
PRODUCTION_CUBE_NAME = 'test_cube'  # name from config file
TEMPLATE_FILE_NAME = 'test_cube.json'


class TestCube(OlapCube):
    def __init__(self):
        path_to_cube_settings = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_NAME)
        path_to_script_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), TEMPLATE_FILE_NAME)
        cube_id = PRODUCTION_CUBE_NAME

        with open(path_to_cube_settings, 'r') as f:
            settings = yaml.load(f)
            cube_settings = settings[cube_id]

        with open(path_to_script_template, 'r') as f:
            full_script_template = SSASTemplate(f.read())

        super().__init__(
            cube_id=cube_id,
            olap_cube_type=OlapCubeType.Tabular,
            cube_settings=cube_settings,
            full_script_template=full_script_template,
        )

    def load(self,
             period: dtu.Period,
             create_partition: bool,
             process_partition: bool,
             process_dimension: bool,
             recalculate_model: bool,
             sync_model: bool,
             ):
        retry = try_except(
            times=3,
            sleep=5,
            exceptions=(DWHError,),
            backoff=False)

        log_message = f'Cube: {self._cube_id}. Processing by sequence.'
        retry_w_time_wrapper = compose(
            retry,
            measure_time(log_message))
        process_tmsl_sequence_w_retry_w_time = retry_w_time_wrapper(self.process_by_sequence)

        process_tmsl_sequence_w_retry_w_time(
            period=period,
            create_partition=create_partition,
            process_partition=process_partition,
            process_dimensions=process_dimension,
            recalculate_model=recalculate_model,
            server_type=ServerTypes.Processing
        )

        if sync_model:
            log_message = f'Cube: {self._cube_id}. Syncing model.'
            retry_w_time_wrapper = compose(
                retry,
                measure_time(log_message))
            sync_tmsl_model_w_retry_w_time = retry_w_time_wrapper(
                self.synchronize_database)

            sync_tmsl_model_w_retry_w_time(
                script_type=ScriptTypes.TMSL
            )
