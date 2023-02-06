import pytest


def test_geoarea_simple(taxi_protocol):
    response = taxi_protocol.get(
        '1.0/get_geoareas?'
        'id=523c7089fd634d33b52a8b29a1d128f1,'
        '7c40f37644374e5784f075d1c4b88547,'
        '27f2578a6e4d4623aeb3c97728b58666',
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'geometry': {
                'shell': [
                    [37.51441, 55.710276],
                    [37.51441, 55.797112],
                    [37.713601, 55.797112],
                    [37.713601, 55.710276],
                    [37.51441, 55.710276],
                ],
                'holes': [],
            },
            '_id': '523c7089fd634d33b52a8b29a1d128f1',
            'name': 'cao',
            'created': '2016-03-10T07:26:21.154+0000',
        },
        {
            'geometry': {
                'shell': [
                    [36.90840238790664, 55.347194847462745],
                    [36.90840238790664, 55.99633617563195],
                    [38.0392689260083, 55.99633617563195],
                    [38.0392689260083, 55.347194847462745],
                    [36.90840238790664, 55.347194847462745],
                ],
                'holes': [],
            },
            '_id': '7c40f37644374e5784f075d1c4b88547',
            'name': 'moscow_activation',
            'created': '2016-10-02T12:37:33.105+0000',
        },
        {
            '_id': '27f2578a6e4d4623aeb3c97728b58666',
            'created': '2017-11-21T14:09:26+0000',
            'geometry': {
                'holes': [],
                'shell': [
                    [37.817173584260395, 55.94891808601154],
                    [37.96754895047132, 55.960474965206224],
                    [37.94633613002967, 55.86953633543438],
                    [37.79630408657265, 55.919886950228346],
                    [37.817173584260395, 55.94891808601154],
                ],
            },
            'name': 'korolev_transfer_removed',
        },
    ]


def test_geoarea_304(taxi_protocol):
    headers = {'If-None-Match': '"a6def25328e2f15ffe521843e7f2f637"'}
    response = taxi_protocol.get(
        '1.0/get_geoareas?'
        'id=523c7089fd634d33b52a8b29a1d128f1,'
        '7c40f37644374e5784f075d1c4b88547,'
        '27f2578a6e4d4623aeb3c97728b58666',
        headers=headers,
    )
    assert response.status_code == 304


def test_geoarea_400(taxi_protocol):
    response = taxi_protocol.get('1.0/get_geoareas')
    assert response.status_code == 400
    assert response.json() == {'error': {'text': 'id is missing in request'}}


def test_geoarea_404(taxi_protocol):
    response = taxi_protocol.get(
        '1.0/get_geoareas?' 'id=523c7089fd634d33b52a8b29a1d128f1,' 'none',
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'can not find docs with ids: none'},
    }


@pytest.mark.parametrize(
    'geoarea_id,localized_name',
    [
        ('523c7089fd634d33b52a8b29a1d128f1', 'Central District'),
        ('9ec8e6f1fd0c4581b869bfd3a568dc82', None),
    ],
)
@pytest.mark.translations(
    subvention_geoareas={'cao': {'ru': 'ЦАО', 'en': 'Central District'}},
)
def test_get_subvention_geoareas(taxi_protocol, geoarea_id, localized_name):
    response = taxi_protocol.get(
        '1.0/get_subvention_geoareas?' 'id=' + geoarea_id,
    )
    assert response.status_code == 200
    subvention_geoareas = response.json()
    for item in subvention_geoareas:
        assert item.get('localized_name') == localized_name
