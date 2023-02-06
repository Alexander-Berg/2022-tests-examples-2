import pytest


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 2,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_periodic_rating_check_task_run(
        testpoint, mockserver, taxi_eats_restapp_marketing, pgsql,
):
    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _mock_rating_info(request):
        res = {'places_rating_info': []}
        rating_test = {'1': 3.0, '2': 3.5, '3': 4.0, '5': 4.0, '6': 3.3}
        for place_id in request.query['place_ids'].split(','):
            res['places_rating_info'].append(
                {
                    'average_rating': rating_test[place_id],
                    'calculated_at': '2021-01-01',
                    'cancel_rating': 4.0,
                    'place_id': int(place_id),
                    'show_rating': True,
                    'user_rating': 4.0,
                },
            )
        return mockserver.make_response(status=200, json=res)

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert(
            updated_at,
            place_id,
            campaign_id,
            group_id,
            ad_id,
            banner_id,
            averagecpc,
            weekly_spend_limit,
            is_active,
            passport_id,
            reason_status
        ) VALUES
        (NOW(), 1, 399264, 4, 5, 1, 1000, 1000000, true, 1229582676, NULL),
        (
            cast('2015-05-01 11:25:00 america/caracas' as TIMESTAMPTZ),
            2, 399265, 4, NULL, NULL,1000, 2000000, true, 1229582678, NULL
        ),
        (NOW(), 3, 399266, 4, 5, 1, 1000, 3000000, true, 1229582676, NULL),
        (NOW(), 4, 399267, 4, 5, NULL, 1000, 4000000, false, NULL, NULL),
        (NOW(), 5, 399268, 4, 5, NULL, 100, 40000, false, NULL, 'low_rating'),
        (NOW(), 6, 399269, 4, 5, NULL, 100, 40000, false, NULL, 'low_rating');
        """,
    )

    @testpoint('rating_check::locked-periodic-finished')
    def handle_finished(arg):
        pass

    await taxi_eats_restapp_marketing.run_periodic_task(
        'eats-restapp-marketing-periodic-rating-check-task-periodic',
    )

    result = handle_finished.next_call()
    assert result == {'arg': 'test'}

    cursor.execute(
        """
        SELECT place_id, is_active, reason_status
        FROM eats_restapp_marketing.advert ORDER BY place_id;
      """,
    )
    res = list(cursor)
    assert len(res) == 6
    assert res[0] == (1, False, 'low_rating')
    assert res[1] == (2, True, None)
    assert res[2] == (3, True, None)
    assert res[3] == (4, False, None)
    assert res[4] == (5, False, None)
    assert res[5] == (6, False, 'low_rating')
    # assert False
