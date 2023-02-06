def remove_not_testable_series(json):
    for series in json['series']:
        remove_not_testable(series)
    return json


def remove_not_testable_promocodes(json):
    for promocode in json['promocodes']:
        remove_not_testable(promocode)
    return json


def remove_not_testable(json):
    # TODO: https://st.yandex-team.ru/TAXIDATA-2410
    del json['created_at']
    del json['updated_at']
    if 'id' in json:
        del json['id']
    return json


async def call_tags_task(stq, stq_runner):
    tags_call = stq.driver_promocodes_upload_tags.next_call()
    await stq_runner.driver_promocodes_upload_tags.call(
        task_id=tags_call['id'],
        args=tags_call['args'],
        kwargs=tags_call['kwargs'],
    )
