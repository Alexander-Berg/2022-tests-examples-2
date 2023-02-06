def get_query(*args, **kwargs):
    conditions = ';'
    query = f"""
    SELECT
        {', '.join(kwargs['params'])}
    FROM contractor_statistics_view.contractors
    WHERE unique_driver_id = \'{kwargs['unique_driver_id']}\'
    """
    if kwargs.get('park_id') and kwargs.get('driver_profile_id'):
        conditions = (
            f' AND park_id = \'{kwargs["park_id"]}\''
            f' AND driver_profile_id = \'{kwargs["driver_profile_id"]}\';'
        )
    elif kwargs.get('unique_driver_id'):
        conditions = (
            f' AND unique_driver_id = \'{kwargs["unique_driver_id"]}\';'
        )

    return query + conditions


async def test_initialize(
        pgsql, stq_runner, unique_drivers, client_events, mockserver,
):
    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def _has_finished_response(request):
        return mockserver.make_response(
            status=200, json={'has_finished': False},
        )

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    unique_drivers.set_retrieve_by_profiles(
        'unique_driver_id', 'driver_profile_id', 'park_id',
    )
    unique_drivers.set_retrieve_by_uniques(
        'unique_driver_id', 'driver_profile_id', 'park_id',
    )
    client_events.status_code = 200
    client_events.response = {'items': [{'status': 'ok', 'version': '777'}]}
    await stq_runner.contractor_statistics_view_initialize.call(
        task_id='task_id',
        args=[],
        kwargs={
            'driver_profile_id': 'driver_profile_id',
            'park_id': 'park_id',
        },
    )

    query = get_query(params=['id'], unique_driver_id='unique_driver_id')

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    assert len(rows) == 1
