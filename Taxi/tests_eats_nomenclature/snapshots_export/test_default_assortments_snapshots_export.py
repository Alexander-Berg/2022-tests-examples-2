import pytest


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_default_assortments.sql'])
async def test_default_assortments_snapshots_export(stq_runner, testpoint):
    brand_id = 777

    logged_default_assortments = []

    @testpoint('yt-logger-default-assortments-snapshot')
    def _yt_logger_default_assortments(data):
        del data['timestamp']
        logged_default_assortments.append(data)

    await stq_runner.eats_nomenclature_export_default_assortments_snapshots.call(  # noqa: E501 pylint: disable=line-too-long
        task_id=str(brand_id), args=[], kwargs={'brand_id': brand_id},
    )

    assert (
        get_sorted_default_assortments(logged_default_assortments)
        == get_expected_def_assortments()
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_default_assortments.sql'])
async def test_stq_error_limit(taxi_config, stq_runner, testpoint):
    @testpoint('export-default-assortments-snapshots-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    brand_id = 777
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_export_default_assortments_snapshots.call(  # noqa: E501 pylint: disable=line-too-long
            task_id=str(brand_id),
            args=[],
            kwargs={'brand_id': brand_id},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_export_default_assortments_snapshots.call(  # noqa: E501 pylint: disable=line-too-long
        task_id=str(brand_id),
        args=[],
        kwargs={'brand_id': brand_id},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


def get_expected_def_assortments():
    return [
        {'assortment_name': 'partner', 'place_id': 1},
        {'assortment_name': 'assortment_name_2', 'place_id': 2},
        {'assortment_name': 'assortment_name_1', 'place_id': 3},
    ]


def get_sorted_default_assortments(default_assortments):
    return sorted(default_assortments, key=lambda item: item['place_id'])
