# pylint: disable=F0401,C5521
import uuid

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest

MOCK_TIME = '2022-02-01T13:53:01+0000'

TAXIMETER_VERSION = 'Taximeter 9.40 (1234)'

UUID1 = '3111340f26fb99e8ee9e63df5ce06899'
DBID1 = '0253f79a86d14b7ab9ac1d5d3017be47'

BASE64_ENCODED_MESSAGE = (
    'Nzc3Nzc3Nzc3Nzc3Nzc3Nz9oZ1mQtVDCQHKYfq0F'
    + 'URlxVcsKIAXZAdgcrDM9D1VP89s7lOV9GnhN651C'
    + 'pscy7U4tczK1zbT0pnyPM+sOWGPvGXVns4kWYB+k'
    + '+Gq3AA0+lRJ/NFE9qYYNmhuYk3O1X3GnAMDa4eC6'
    + '30OUkBIXpNE='
)


@pytest.mark.now(MOCK_TIME)
async def test_generate_qr_code(
        taxi_grocery_pro_misc, dap, testpoint, load_binary,
):
    driver_uuid = UUID1
    driver_dbid = DBID1
    taxi_grocery_pro_misc = dap.create_driver_wrapper(
        taxi_grocery_pro_misc,
        driver_uuid=driver_uuid,
        driver_dbid=driver_dbid,
    )

    @testpoint('testpoint_check_raw_data')
    def check_raw_data(data):
        assert (
            data['raw_data']
            == driver_dbid + '_' + driver_uuid + '\t' + MOCK_TIME
        )

    @testpoint('rewrite_random_iv')
    def rewrite_random_iv(data):
        pass

    response = await taxi_grocery_pro_misc.get(
        '/driver/v1/grocery-misc/v1/qr',
        headers={'User-Agent': TAXIMETER_VERSION},
    )
    assert response.status_code == 200
    assert check_raw_data.times_called == 1
    assert rewrite_random_iv.times_called == 1

    assert response.content == load_binary('demo.png')


@pytest.mark.now(MOCK_TIME)
async def test_generate_correct_100(
        taxi_grocery_pro_misc, dap, testpoint, load_binary,
):
    driver_dbid = DBID1

    for num in range(100):
        driver_uuid = str(uuid.uuid1(1337, num))
        response = (
            await dap.create_driver_wrapper(
                taxi_grocery_pro_misc,
                driver_uuid=driver_uuid,
                driver_dbid=driver_dbid,
            ).get(
                '/driver/v1/grocery-misc/v1/qr',
                headers={'User-Agent': TAXIMETER_VERSION},
            )
        )
        assert response.status_code == 200


@pytest.mark.now(MOCK_TIME)
async def test_decode_basic_200(taxi_grocery_pro_misc):
    decode_response = await taxi_grocery_pro_misc.post(
        '/internal/grocery-misc/v1/hack-qr-pls',
        json={'qr_content': BASE64_ENCODED_MESSAGE},
    )

    assert decode_response.status_code == 200
    assert decode_response.json()['dbid_uuid'] == DBID1 + '_' + UUID1
    assert decode_response.json()['timestamp'] == MOCK_TIME


@pytest.mark.now(MOCK_TIME)
async def test_decode_basic_400(taxi_grocery_pro_misc):
    for broken_symbol, _ in enumerate(BASE64_ENCODED_MESSAGE):
        msg = (
            BASE64_ENCODED_MESSAGE[:broken_symbol]
            + ('a' if BASE64_ENCODED_MESSAGE[broken_symbol] != 'a' else 'b')
            + BASE64_ENCODED_MESSAGE[broken_symbol + 1 :]
        )

        decode_response = await taxi_grocery_pro_misc.post(
            '/internal/grocery-misc/v1/hack-qr-pls', json={'qr_content': msg},
        )
        assert decode_response.status_code == 400
