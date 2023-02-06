import pytest


@pytest.mark.parametrize(
    'value,output',
    [
        ('1.234', '1.234'),
        ('1.2345', '1.2345'),
        ('1.0', '1'),
        ('1', '1'),
        ('0.0', '0'),
        ('0.0000', '0'),
    ],
)
async def test_decimal64_ok(taxi_userver_sample, value, output, mockserver):
    @mockserver.json_handler('/userver-sample/decimal')
    async def _mock(request):
        return {'cost': value, 'units': value}

    response = await taxi_userver_sample.post(
        'decimal', params={'cost': value}, json={'units': value},
    )
    assert response.status_code == 200
    assert response.json() == {'cost': output, 'units': output}


@pytest.mark.parametrize(
    'value,output', [('-1.2345', '-1.2345'), ('-1.0', '-1'), ('-0.0', '0')],
)
async def test_decimal64_ok_negative(
        taxi_userver_sample, value, output, mockserver,
):
    @mockserver.json_handler('/userver-sample/decimal')
    async def _mock(request):
        return {'cost': '0', 'units': value}

    response = await taxi_userver_sample.post(
        'decimal', params={'cost': '0'}, json={'units': value},
    )
    assert response.status_code == 200
    assert response.json() == {'cost': '0', 'units': output}


@pytest.mark.parametrize(
    'value',
    [
        'fake',
        '0.01d',
        '0d0',
        '',
        '-',
        '.0',
        '.01',
        '.1',
        '.',
        '1.',
        'o0.1',
        '1o.0',
        '0.00001',
        '12345678901234567890123456789.0000',
        '-1.2345',
        '-1.0',
        '-0.0',
    ],
)
async def test_decimal64_fail(taxi_userver_sample, value):
    response = await taxi_userver_sample.post(
        'decimal', params={'cost': value}, json={'units': value},
    )
    assert response.status_code == 400
