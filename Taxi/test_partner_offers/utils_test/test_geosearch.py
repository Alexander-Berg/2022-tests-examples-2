import aiohttp
import pytest

from partner_offers import geosearch_parsing


async def test_get_organization_by_oid(web_context, mockserver, load_json):
    test_business_oid = 1255966696
    stub = load_json('stub_business_oid_search.json')

    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return aiohttp.web.json_response(stub)

    org_data, loc_data = await geosearch_parsing.search_organization(
        test_business_oid, 'ru', web_context,
    )
    uri = 'https://avatars.mds.yandex.net/get-altay/1881734/2a0000016a35aba90cfe1b24c59b99f31939/M'  # noqa: E501
    assert org_data == geosearch_parsing.OrganizationData(
        name='Магнит', logo_uri=uri, chain_id=35471869327,
    )
    assert loc_data.work_times
    loc_data.work_times = []  # tested in other test
    assert loc_data == geosearch_parsing.LocationData(
        name='Магнит',
        business_oid=test_business_oid,
        longitude=39.734711,
        latitude=43.572154,
        country='Россия',
        city='Сочи',
        formatted_address='Россия, Краснодарский край, Сочи, Курортный проспект, 73',  # noqa: E501
        logo_uri=uri,
        work_times=[],
        timezone_offset=10800,
        chain=geosearch_parsing.ChainData(chain_id=35471869327, name='Магнит'),
    )


async def test_search_chains(web_context, mockserver, load_json):
    chain_id = 35471869327
    stub = load_json('stub_chain_search.json')

    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return aiohttp.web.json_response(stub)

    locations = await geosearch_parsing.get_locations_of_organization(
        chain_id, 'ru', web_context,
    )
    expected = len(stub['features'])
    assert len(locations) == expected
    for loc in locations:
        assert isinstance(loc.name, str), loc
        assert isinstance(loc.business_oid, int), loc
        assert isinstance(loc.longitude, float), loc
        assert isinstance(loc.latitude, float), loc
        assert isinstance(loc.work_times, list), loc
        assert isinstance(loc.formatted_address, str), loc


@pytest.mark.parametrize('stub_replace', [None, 'remove', []])
async def test_organization_not_found(
        web_context, mockserver, load_json, stub_replace,
):
    test_business_oid = 1255966696
    response = load_json('stub_business_oid_search.json')
    if stub_replace == 'remove':
        del response['features']
    else:
        response['features'] = stub_replace

    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return aiohttp.web.json_response(response)

    res = await geosearch_parsing.search_organization(
        test_business_oid, 'ru', web_context,
    )
    assert res is None


async def test_locations_by_id(cron_context, mockserver, load_json):
    response = load_json('stub_chain_search.json')
    business_oids = [
        1253355814,
        1551162356,
        1623619772,
        34844489391,
        65042514136,
        162496914873,
        174536654624,
    ]

    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return response

    res = await geosearch_parsing.get_locations_by_ids(
        business_oids, 'ru', cron_context,
    )
    assert {x.business_oid for x in res} == set(business_oids)


@pytest.mark.now('2019-10-24T12:08:12')
@pytest.mark.parametrize(
    'working_hours,expected',
    [
        (None, []),
        (
            [
                {
                    'Intervals': [{'from': '09:00:00', 'to': '18:00:00'}],
                    'Tuesday': 1,
                    'Wednesday': 1,
                },
                {
                    'Intervals': [{'from': '09:00:00', 'to': '19:00:00'}],
                    'Thursday': 1,
                },
                {
                    'Friday': 1,
                    'Intervals': [{'from': '09:00:00', 'to': '18:00:00'}],
                },
                {
                    'Intervals': [{'from': '10:00:00', 'to': '18:00:00'}],
                    'Saturday': 1,
                    'Sunday': 1,
                },
            ],
            [
                (1571896800, 1571929200),
                (1571983200, 1572015600),
                (1572073200, 1572102000),
                (1572159600, 1572188400),
                (1572328800, 1572361200),
                (1572415200, 1572451200),
            ],
        ),
        (
            [
                {
                    'Everyday': 1,
                    'Intervals': [{'from': '10:00:00', 'to': '17:50:00'}],
                },
            ],
            [
                (1571900400, 1571928600),
                (1571986800, 1572015000),
                (1572073200, 1572101400),
                (1572159600, 1572187800),
                (1572246000, 1572274200),
                (1572332400, 1572360600),
                (1572418800, 1572447000),
            ],
        ),
        (
            [
                {
                    'Intervals': [
                        {'from': '09:00:00', 'to': '11:00:00'},
                        {'from': '12:00:00', 'to': '13:00:00'},
                        {'from': '15:00:00', 'to': '20:00:00'},
                    ],
                    'Tuesday': 1,
                    'Wednesday': 1,
                },
                {
                    'Intervals': [{'from': '15:00:00', 'to': '00:00:00'}],
                    'Friday': 1,
                },
            ],
            [
                (1571896800, 1571904000),
                (1571907600, 1571911200),
                (1571918400, 1571936400),
                (1572004800, 1572037200),
                (1572328800, 1572336000),
                (1572339600, 1572343200),
                (1572350400, 1572368400),
            ],
        ),
        ([{'TwentyFourHours': 1, 'Everyday': 1}], [(1571864400, 1572469200)]),
    ],
)
async def test_parse_working_hours(
        web_context, mockserver, load_json, working_hours, expected,
):
    test_business_oid = 1255966696
    raw_response = load_json('stub_business_oid_search.json')
    company_meta = raw_response['features'][0]['properties']['CompanyMetaData']
    if working_hours is None:
        del company_meta['Hours']
    else:
        company_meta['Hours']['Availabilities'] = working_hours

    # pylint: disable=unused-variable
    @mockserver.json_handler('/geocoder/yandsearch')
    def get_by_business_oid(request):
        return aiohttp.web.json_response(raw_response)

    _, loc_data = await geosearch_parsing.search_organization(
        test_business_oid, 'ru', web_context,
    )

    assert loc_data.work_times == expected
