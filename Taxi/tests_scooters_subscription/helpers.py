import typing


TEST_UID = '123454321'
TEST_TICKET = 'билет_на_балет.на_трамвай_билета_нет'
TEST_POSITION = '42.594652,56.840232'
TEST_GEOBASE_IDS_PATH = [160375, 98793, 10687, 3, 225, 10001, 10000]

HEADERS = {'X-Yandex-UID': TEST_UID, 'X-Ya-User-Ticket': TEST_TICKET}


def assert_response(response, expected):
    code, body = expected
    assert {
        'code': response.status_code,
        'body': (
            response.text
            if isinstance(body, str) or not response.text
            else response.json()
        ),
    } == {'code': code, 'body': body}


async def get_offer_params_check(
        taxi_scooters_subscription, expected: typing.Tuple[int, typing.Dict],
):
    response = await taxi_scooters_subscription.get(
        '/scooters-subscriptions/v1/subscriptions/offer-params',
        params={'position': '42.4961,56.7523'},
        headers=HEADERS,
    )
    assert_response(response, expected)


async def fetch_metric(
        taxi_scooters_subscription,
        taxi_scooters_subscription_monitor,
        get_single_metric_by_label_values,
):
    await taxi_scooters_subscription.tests_control(reset_metrics=True)
    await taxi_scooters_subscription.run_distlock_task(
        'scooters-subscription-metrics-collector',
    )

    result = {}
    for status in ('processing', 'ready', 'cancelling', 'refunding'):
        metric = await get_single_metric_by_label_values(
            taxi_scooters_subscription_monitor,
            sensor='scooters_subscription_by_status',
            labels={'status': status},
        )
        if metric.value:  # omit zeroes, but ensure `metric is not Null`
            result[status] = metric.value
    return result


def mock_offers(
        mockserver, offers, language='RU', unauthorized=False, regions=None,
):
    @mockserver.json_handler('/mediabilling/offers/composite')
    async def _mediabilling_composite_offers(request):
        hierarchy = ','.join(map(str, regions or TEST_GEOBASE_IDS_PATH))
        expected_query = {
            'target': 'andrei',
            'features': 'basic-plus',
            'regionHierarchy': hierarchy,
            'language': language,
        }
        if not unauthorized:
            expected_query['uid'] = TEST_UID
        assert request.query == expected_query
        return mockserver.make_response(
            status=200, json={'result': {'offers': offers}},
        )


def mock_intervals(
        mockserver, features: typing.List[str] = None, purchase=None,
):
    @mockserver.json_handler('/mediabilling/billing/intervals')
    async def _intervals(request):
        assert request.query == {'__uid': TEST_UID}

        interval = {
            'start': '2022-02-09T01:02:03Z',
            'end': '2022-02-19T04:05:06Z',
        }
        return mockserver.make_response(
            status=200,
            json={
                'invocationInfo': {'req-id': 'test-req-id'},
                'result': {
                    'intervals': [
                        {
                            'start': '2022-02-09T01:02:03Z',
                            # ends 1s before NOW
                            'end': '2022-02-18T02:47:59+03:00',
                            'orderInfo': {
                                'productInfo': {
                                    'id': 'obsolete',
                                    'price': {
                                        'currency': 'KOPEYKI',
                                        'amount': 31.0,
                                    },
                                    'promoTrial': False,
                                    'features': features or [],
                                },
                                'introInterval': interval,
                                'trialInterval': interval,
                                'nextPayment': '2019-07-09T18:51:32Z',
                            },
                        },
                        {
                            **interval,
                            'orderInfo': {
                                'productInfo': {
                                    'id': 'ru.y1231231.12312',
                                    'price': {
                                        'currency': 'RUB',
                                        'amount': 169.0,
                                    },
                                    'promoTrial': False,
                                    'features': [
                                        'some',
                                        *(features or []),
                                        'another',
                                    ],
                                },
                                'introInterval': (
                                    interval if purchase == 'intro' else None
                                ),
                                'trialInterval': (
                                    interval if purchase == 'trial' else None
                                ),
                                'nextPayment': '2019-07-09T18:51:32Z',
                            },
                        },
                    ],
                },
            },
        )
