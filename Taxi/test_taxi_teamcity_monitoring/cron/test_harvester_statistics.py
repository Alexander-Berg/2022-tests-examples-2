import functools

from aiohttp import web
import pytest

from taxi_teamcity_monitoring.generated.cron import run_cron


@pytest.mark.now('2018-10-05T06:00:00')
@pytest.mark.config(TEAMCITY_MONITORING_HARVESTER_STAT_ENABLED=True)
async def test_harvester_statistics(
        load, load_json, mock_solomon, mock_teamcity,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    @mock_generator
    def teamcity_request(request):
        for filename in [
                'teamcity_uservices.json',
                'teamcity_uservices_bionic.json',
                'teamcity_py3.json',
        ]:
            yield load_json(filename)

    @mock_teamcity('/repository/download', prefix=True)
    def teamcity_download_request(request):
        if request.path.endswith('/uservices_files_size'):
            filename = 'uservices_files_size'
        elif request.path.endswith('/commit_info/changed_paths.txt'):
            if '/1661883:id/' in request.path_qs:
                return web.Response(
                    status=404,
                    body='not found',
                    headers={'Content-Type': 'text/html;charset=ISO-8859-1'},
                )
            filename = 'changed_files'
        else:
            raise ValueError(f'unknown path suffix in {request.path}')

        return web.Response(
            body=load(filename), headers={'Content-Type': 'text/plain'},
        )

    @mock_solomon('/api/v2/push')
    @mock_generator
    def handler(request):
        solomon_json = load_json('solomon_request.json')
        for expected_json in solomon_json:
            assert request.json == expected_json
            request = yield {'sensorsProcessed': len(request.json['sensors'])}

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'harvester_statistics.run_harvester_statistics',
            '-t',
            '0',
            '--debug',
        ],
    )

    assert teamcity_request.next_call()['request'].path_qs == (
        '/teamcity/app/rest/builds?locator=status:SUCCESS,buildType'
        '(id:YandexTaxiProjects_UservicesArcadia_Internal_StatisticsArcadia_'
        'Common)'
        ',branch:default:any,count:100,lookupLimit:1000&fields=build'
        '(id,lastChanges(change(date)),startDate,buildTypeId,'
        'statistics(property))'
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        '/teamcity/app/rest/builds?locator=status:SUCCESS,buildType'
        '(id:YandexTaxiProjects_UservicesArcadia_Internal_StatisticsArcadia_'
        'Common_Bionic)'
        ',branch:default:any,count:100,lookupLimit:1000&fields=build'
        '(id,lastChanges(change(date)),startDate,buildTypeId,'
        'statistics(property))'
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        '/teamcity/app/rest/builds?locator=status:SUCCESS,buildType'
        '(id:YandexTaxiProjects_TaxiBackendPy3_Internal_Statistics_Common)'
        ',branch:default:any,count:100,lookupLimit:1000&fields=build'
        '(id,lastChanges(change(date)),startDate,buildTypeId,'
        'statistics(property))'
    )
    assert not teamcity_request.has_calls
    assert teamcity_download_request.times_called == 19
    assert handler.times_called == 33


def mock_generator(func):
    generator = None

    @functools.wraps(func)
    def wrapper(request):
        nonlocal generator
        if generator is None:
            generator = func(request)
            return next(generator)
        return generator.send(request)

    return wrapper
