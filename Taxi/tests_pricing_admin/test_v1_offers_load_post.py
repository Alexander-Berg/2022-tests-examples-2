import pytest


def get_loads(pgsql, user, date):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM ONLY cache.offers_loads '
            f'WHERE user_id=%s AND table_name=%s',
            (user, date),
        )
        fields = [column.name for column in cursor.description]
        db_result = cursor.fetchall()
        return {field: value for field, value in zip(fields, db_result[0])}


@pytest.mark.parametrize(
    'user_id, date, response_code, base',
    [
        (
            'user1',
            '2021-09-19',
            200,
            {
                'table_name': '2021-09-19',
                'user_id': 'user1',
                'yql_error': None,
                'yql_link': 'link_user1',
                'yql_share_link': 'share_user1',
            },
        ),
        (
            'user2',
            '2021-09-21',
            208,
            {
                'table_name': '2021-09-21',
                'user_id': 'user2',
                'yql_error': None,
                'yql_link': 'link2',
                'yql_share_link': 'sharelink2',
            },
        ),
        (
            'user1',
            '2021-09-21',
            200,
            {
                'table_name': '2021-09-21',
                'user_id': 'user1',
                'yql_error': None,
                'yql_link': 'link_user1',
                'yql_share_link': 'share_user1',
            },
        ),
    ],
    ids=['only', 'duplicated', 'renew'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
async def test_v1_offers_load_post(
        taxi_pricing_admin,
        pgsql,
        user_id,
        date,
        response_code,
        mockserver,
        base,
):
    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_yql_run(request):
        data = request.json
        assert (
            data['content'].replace('\n', '') == ''
            'PRAGMA yt.TmpFolder="//home/taxi/testsuite/tmp/pricing-admin";'
            ' PRAGMA yson.DisableStrict;$bv = SELECT    `caller_link`,    '
            '`prepare_link`,    `data`,    `uuid`,    `user_id`,    '
            '`timestamp`,'
            '    `category_name`FROM hahn.`home/testsuite/pricing-data-'
            'preparer-yandex-taxi-backend-variables-json-log/1d/{0}`'
            'WHERE user_id=\'{1}\' '
            'AND source=\'v2/prepare\';'
            '$links = SELECT caller_link FROM $bv;'
            '$uuids = SELECT `uuid` FROM $bv;'
            'SELECT * FROM $bv;SELECT *FROM hahn.`home/testsuite/'
            'pricing-data-preparer-yandex-taxi-v2-prepare-common'
            '-json-log/1d/{0}`'
            ' WHERE caller_link IN $links;'
            'SELECT *FROM hahn.`home/testsuite/'
            'pricing-data-preparer-yandex-taxi-v2-prepare-'
            'category-info-json-log/1d/{0}` WHERE caller_link IN $links AND'
            ' `uuid` IN $uuids'
            ';'.format(date, user_id)
        )
        return {'id': 'link_' + user_id}

    @mockserver.json_handler('/yql/api/v2/operations/link_user1/share_id')
    def _mock_user1_share_id(request):
        return 'share_user1'

    response = await taxi_pricing_admin.post(
        'v1/offers/load', params={'user_id': user_id, 'date': date},
    )
    assert response.status_code == response_code

    assert get_loads(pgsql, user_id, date) == base
