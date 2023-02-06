import pytest


def make_campaign(
        name='рога и копыта', averagecrc=1000000, weekly_spend_limit=None,
) -> dict:
    result = {
        'method': 'add',
        'params': {
            'Campaigns': [
                {
                    'Name': 'EDA_2',
                    'StartDate': '2020-12-04',
                    'ClientInfo': name,
                    'ContentPromotionCampaign': {
                        'BiddingStrategy': {
                            'Network': {'BiddingStrategyType': 'SERVING_OFF'},
                            'Search': {
                                'AverageCpc': {
                                    'AverageCpc': averagecrc,
                                    'WeeklySpendLimit': weekly_spend_limit,
                                },
                                'BiddingStrategyType': 'AVERAGE_CPC',
                            },
                        },
                    },
                },
            ],
        },
    }

    return result


def make_add_result(identificator, warnings=None, errors=None) -> dict:
    result = {
        'result': {
            'AddResults': [
                {'Id': identificator, 'Warnings': warnings, 'Errors': errors},
            ],
        },
    }
    return result


@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.parametrize(
    'advert_ids,campaign_ids',
    [
        pytest.param(
            [1, 2, 3],
            [(100,), (200,), (3300,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_null_id_null.sql'],
                ),
            ],
            id='uuid null campaign id null',
        ),
        pytest.param(
            [1, 2, 3],
            [(11,), (22,), (333,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_null_id_value.sql'],
                ),
            ],
            id='uuid null campaign id value',
        ),
        pytest.param(
            [1, 2, 3],
            [(100,), (100,), (100,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_value_id_null.sql'],
                ),
            ],
            id='uuid value campaign id null',
        ),
        pytest.param(
            [1, 2, 3],
            [(11,), (22,), (333,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_value_id_value.sql'],
                ),
            ],
            id='uuid value campaign id value',
        ),
        pytest.param(
            [1, 2, 3],
            [(100,), (200,), (3300,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_value_multi_all.sql'],
                ),
            ],
            id='uuid value multi all',
        ),
        pytest.param(
            [1, 2, 3],
            [(100,), (200,), (100,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_value_multi_part.sql'],
                ),
            ],
            id='uuid value multi part',
        ),
        pytest.param(
            [1, 2, 3],
            [(11,), (11,), (11,)],
            marks=[
                pytest.mark.pgsql(
                    'eats_restapp_marketing',
                    files=['insert_uuid_value_id_one.sql'],
                ),
            ],
            id='attach not null campaign from null',
        ),
    ],
)
async def test_run_create_tasks(
        testpoint,
        taxi_eats_restapp_marketing,
        pgsql,
        mockserver,
        mock_places_handle,
        advert_ids,
        campaign_ids,
):
    @mockserver.json_handler('/direct/json/v5/campaignsext')
    async def __handle_create_campaign(request):
        assert request.headers['Authorization'].count('Bearer') == 1
        names = request.json['params']['Campaigns'][0]['Name'].split('_')
        # умножение для place_id != campaign_id
        campaign_id = int(names[1]) * 100
        assert len(names) == 2
        return mockserver.make_response(
            status=200, json=make_add_result(campaign_id),
        )

    @testpoint('run-create-tasks-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT campaign_id FROM eats_restapp_marketing.advert '
            'WHERE id in ({})'.format(','.join(str(id) for id in advert_ids)),
        )
        assert list(cursor) == campaign_ids

        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
            SELECT creation_started
            FROM eats_restapp_marketing.advert_for_create
            """,
        )
        assert list(cursor) == [(True,), (True,), (True,)]

    async with taxi_eats_restapp_marketing.spawn_task('run-create-tasks'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def request_proxy_create_bulk(
        taxi_eats_restapp_marketing, partner_id, body,
):
    url = '/4.0/restapp-front/marketing/v1/ad/cpm/create-bulk'
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
        'Authorization': 'token',
        'X-Remote-IP': '127.0.0.1',
    }
    extra = {'headers': headers, 'json': body}

    return await taxi_eats_restapp_marketing.post(url, **extra)


pytest.mark.now('2022-05-04T12:00:00+03:00')
