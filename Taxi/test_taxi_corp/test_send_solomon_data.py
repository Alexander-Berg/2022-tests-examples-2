# pylint: disable=redefined-outer-name, too-many-locals
import pytest

from taxi_corp import cron_run


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize(
    ['expected_result'],
    [({'experiments.replace_phone_to_phone_id_error_count': 0},)],
)
async def test_send_solomon_data(patch, expected_result):
    module = 'taxi_corp.stuff.send_solomon_data'

    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(push_data, *args, **kwargs):
        json = push_data.as_dict()
        sensors = json['sensors']
        for sensor in sensors:
            sensor_value = sensor['value']
            sensor_name = sensor['labels']['sensor']
            passed_application = sensor['labels']['application']

            assert passed_application == cron_run.CORP_APPLICATION_NAME
            assert sensor_name.startswith(module)

            clean_sensor_name = sensor_name[len(module) + 1 :]
            assert (
                expected_result[clean_sensor_name] == sensor_value
            ), clean_sensor_name

    await cron_run.main([module, '-t', '0'])
