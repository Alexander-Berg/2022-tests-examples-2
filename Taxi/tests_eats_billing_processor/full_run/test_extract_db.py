# pylint: disable=import-only-modules
from datetime import datetime
from datetime import timedelta
import json
import os


from psycopg2.extras import RealDictCursor
import pytest

from tests_eats_billing_processor.full_run import extract_db
# pylint: enable=import-only-modules


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={'create_handler_enabled': True},
)
async def test_extract_db(full_run_fixtures, pgsql):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    input_requests = json.load(open(os.path.join(cur_dir, 'input.json')))
    for request in input_requests:
        response = await full_run_fixtures.taxi_eats_billing_processor.post(
            '/v1/create', json=request,
        )
        assert response.status == 200

    cursor = pgsql['eats_billing_processor'].cursor(
        cursor_factory=RealDictCursor,
    )

    class MyArgs:
        def __init__(self):
            self.order_nr = None
            self.ids = None

    args = MyArgs()
    args.ids = [1, 3, 4, 5]
    input_requests.pop(1)
    result = extract_db.get_json_from_db(cursor, args)

    # хак на коррекцию времени, которая происходит когда через ручку
    # дата записывается в БД
    correction = timedelta(hours=3)
    for request in input_requests:
        date = datetime.strptime(request['event_at'], '%Y-%m-%dT%H:%M:%SZ')
        request['event_at'] = (date + correction).strftime(
            '%Y-%m-%dT%H:%M:%SZ',
        )
    assert input_requests == json.loads(result)
