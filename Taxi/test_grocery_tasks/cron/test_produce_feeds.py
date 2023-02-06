import pytest

from taxi.clients import mds_s3

from grocery_tasks.generated.cron import run_cron


@pytest.mark.config(
    GROCERY_TASKS_ENABLED_CRONS={'produce_grocery_feeds': True},
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
async def test_produce_feeds(
        mockserver, cron_runner, load_json, load_binary, patch,
):
    expected_uploads = {
        'grocery_feed_google_213.csv': load_binary('google.csv').decode(
            'utf-8',
        ),
        'grocery_feed_google_2.csv': load_binary('google.csv').decode('utf-8'),
        'grocery_feed_fb_213.xml': load_binary('fb.xml').decode('utf-8')[:-1],
        'grocery_feed_fb_2.xml': load_binary('fb.xml').decode('utf-8')[:-1],
        'grocery_feed_direct_213.xml': load_binary('direct_msk.xml').decode(
            'utf-8',
        )[:-1],
        'grocery_feed_direct_2.xml': load_binary('direct_spb.xml').decode(
            'utf-8',
        )[:-1],
    }

    uploads = {}

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(key, body, *args, **kwargs):
        uploads[key] = body
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    @mockserver.json_handler('/overlord-catalog-feeds/feeds/raw_items_data')
    async def _raw_items(request):
        return load_json('feeds_raw.json')

    @mockserver.json_handler('/overlord-catalog/admin/catalog/v1/countries')
    async def _countries(request):
        return {'countries': [{'country_id': '0', 'name': 'Россия'}]}

    @mockserver.json_handler('/overlord-catalog/admin/catalog/v1/cities')
    async def _cities(request):
        return {
            'cities': [
                {'city_id': '213', 'name': 'Москва'},
                {'city_id': '2', 'name': 'Санкт-Петербург'},
            ],
        }

    await run_cron.main(
        ['grocery_tasks.crontasks.produce_grocery_feeds', '-t', '0'],
    )
    assert uploads == expected_uploads
