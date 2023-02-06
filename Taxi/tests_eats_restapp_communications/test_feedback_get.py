import pytest

PARTNER_ID = 42
KNOWN_SLUGS = ['dashboard', 'orders']


def get_feedback_settings(**slug_conditions):
    conditions = []
    for slug, cond in slug_conditions.items():
        if isinstance(cond, dict):
            cond.update({'slug': slug})
            conditions.append(cond)
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_restapp_communications_feedbacks_settings',
        consumers=['eats_restapp_communications/partner_id'],
        clauses=[],
        default_value={
            'known_slugs': KNOWN_SLUGS,
            'fresh_conditions': conditions,
        },
    )


@pytest.mark.parametrize(
    'slug',
    [
        pytest.param(
            'dashboard',
            marks=(
                get_feedback_settings(
                    abacaba={'start_date': '2022-03-01T00:00:00+00'},
                )
            ),
            id='with settings for other slug',
        ),
        pytest.param(
            'dashboard',
            marks=(
                get_feedback_settings(
                    dashboard={'start_date': '2022-03-01T00:00:00+00'},
                )
            ),
            id='with settings for correct slug',
        ),
    ],
)
async def test_without_feedback_always_returns_not_fresh(
        taxi_eats_restapp_communications, slug,
):
    response = await taxi_eats_restapp_communications.get(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'slug': slug},
    )
    assert response.status_code == 200
    body = response.json()
    assert not body['is_fresh']
    assert 'score' not in body
    assert 'created' not in body
    assert 'comment' not in body


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_add_feedbacks.sql',),
)
@pytest.mark.parametrize(
    'slug, is_fresh, score, comment',
    [
        pytest.param(
            'dashboard',
            True,
            5,
            'comment_new',
            marks=(
                get_feedback_settings(
                    abacaba={'start_date': '2022-03-01T00:00:00+00'},
                )
            ),
            id='with settings for other slug',
        ),
        pytest.param(
            'dashboard',
            True,
            5,
            'comment_new',
            marks=(get_feedback_settings(dashboard={})),
            id='with settings for correct slug, but empty start_date',
        ),
        pytest.param(
            'dashboard',
            True,
            5,
            'comment_new',
            marks=(
                get_feedback_settings(
                    dashboard={'start_date': '2022-01-01T00:00:00+00'},
                )
            ),
            id='with settings for correct slug, older start_date',
        ),
        pytest.param(
            'dashboard',
            False,
            5,
            'comment_new',
            marks=(
                get_feedback_settings(
                    dashboard={'start_date': '2022-03-01T00:00:00+00'},
                )
            ),
            id='with settings for correct slug, newer start_date',
        ),
    ],
)
async def test_with_feedback_returns_correct_is_fresh(
        taxi_eats_restapp_communications, slug, is_fresh, score, comment,
):
    response = await taxi_eats_restapp_communications.get(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'slug': slug},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['is_fresh'] == is_fresh
    if score:
        assert body['score'] == score
        assert 'created' in body
    else:
        assert 'score' not in body
        assert 'created' not in body
    if comment:
        assert body['comment'] == comment
    else:
        assert 'comment' not in body


async def test_feedback_no_partner_id(taxi_eats_restapp_communications):
    response = await taxi_eats_restapp_communications.get(
        '/4.0/restapp-front/communications/v1/feedback',
        params={'slug': 'dashboard'},
    )
    assert response.status_code == 400


async def test_feedback_invalid_slug(taxi_eats_restapp_communications):
    response = await taxi_eats_restapp_communications.get(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'slug': 'abacaba'},
    )
    assert response.status_code == 400
