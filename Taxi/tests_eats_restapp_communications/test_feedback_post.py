from dateutil import parser
import pytest

PARTNER_ID = 42
KNOWN_SLUGS = ['dashboard']


def get_feedback_settings(comment_limit, score_min, score_max):
    value = {'known_slugs': KNOWN_SLUGS}
    if comment_limit:
        value['comment_limit'] = comment_limit
    if score_min:
        value['score_min'] = score_min
    if score_max:
        value['score_max'] = score_max
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_restapp_communications_feedbacks_settings',
        consumers=['eats_restapp_communications/partner_id'],
        clauses=[],
        default_value=value,
    )


def make_len_string(length: int):
    return ''.join(str(i % 10) for i in range(length))


def get_feedbacks_from_db(pgsql, partner_id, slug):
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        'SELECT score, comment, created_at '
        'FROM eats_restapp_communications.feedbacks '
        'WHERE partner_id = %s AND slug = %s',
        (partner_id, slug),
    )
    return list(cursor)


@pytest.mark.parametrize(
    'slug, score, comment, saved_comment',
    [
        pytest.param(
            'dashboard',
            4,
            None,
            None,
            marks=(get_feedback_settings(None, None, None)),
            id='empty comment, empty config',
        ),
        pytest.param(
            'dashboard',
            4,
            None,
            None,
            marks=(get_feedback_settings(None, None, None)),
            id='empty comment, limit in config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(9),
            make_len_string(9),
            marks=(get_feedback_settings(None, None, None)),
            id='short comment, empty config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(9),
            make_len_string(9),
            marks=(get_feedback_settings(10, None, None)),
            id='short comment, limit in config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(11),
            make_len_string(11),
            marks=(get_feedback_settings(None, None, None)),
            id='long comment, empty config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(11),
            make_len_string(10),
            marks=(get_feedback_settings(10, None, None)),
            id='long comment, limit in config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(1111),
            make_len_string(1000),
            marks=(get_feedback_settings(None, None, None)),
            id='ultra long comment, empty config',
        ),
        pytest.param(
            'dashboard',
            4,
            make_len_string(1111),
            make_len_string(10),
            marks=(get_feedback_settings(10, None, None)),
            id='ultra long comment, limit in config',
        ),
    ],
)
async def test_feedback_save_success(
        taxi_eats_restapp_communications,
        pgsql,
        slug,
        score,
        comment,
        saved_comment,
):
    request = {'slug': slug, 'score': score}
    if comment:
        request['comment'] = comment
    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json=request,
    )

    assert response.status_code == 200
    body = response.json()
    assert body['is_fresh']
    assert body['score'] == score
    if saved_comment:
        assert body['comment'] == saved_comment

    stored = get_feedbacks_from_db(pgsql, PARTNER_ID, slug)
    assert stored == [(score, saved_comment, parser.parse(body['created']))]


@pytest.mark.parametrize(
    'slug',
    [
        pytest.param(
            'dashboard', marks=(get_feedback_settings(None, None, None)),
        ),
    ],
)
async def test_feedback_double_save(
        taxi_eats_restapp_communications, pgsql, slug,
):
    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'slug': 'dashboard', 'score': 3},
    )
    assert response.status_code == 200
    first_date = parser.parse(response.json()['created'])
    assert len(get_feedbacks_from_db(pgsql, PARTNER_ID, 'dashboard')) == 1

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'slug': 'dashboard', 'score': 3},
    )
    assert response.status_code == 200
    second_date = parser.parse(response.json()['created'])
    assert len(get_feedbacks_from_db(pgsql, PARTNER_ID, 'dashboard')) == 2

    assert second_date > first_date


async def test_feedback_no_partner_id(taxi_eats_restapp_communications):
    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        json={'slug': 'dashboard', 'score': 3},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'slug',
    [
        pytest.param('dashboard', id='known slug, no config'),
        pytest.param(
            'abacaba',
            marks=(get_feedback_settings(None, None, None)),
            id='unknown slug, nonempty config',
        ),
    ],
)
async def test_feedback_invalid_slug(taxi_eats_restapp_communications, slug):
    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'slug': slug, 'score': 3},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'score',
    [
        pytest.param(0, id='score less than limit, no config'),
        pytest.param(
            0,
            marks=(get_feedback_settings(None, None, None)),
            id='score less than limit, empty config',
        ),
        pytest.param(
            1,
            marks=(get_feedback_settings(None, 2, None)),
            id='score less than limit, limit in config',
        ),
        pytest.param(6, id='score greater than limit, no config'),
        pytest.param(
            6,
            marks=(get_feedback_settings(None, None, None)),
            id='score greater than limit, empty config',
        ),
        pytest.param(
            5,
            marks=(get_feedback_settings(None, None, 4)),
            id='score greater than limit, limit in config',
        ),
    ],
)
async def test_feedback_invalid_score(taxi_eats_restapp_communications, score):
    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/feedback',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={'slug': 'dashboard', 'score': score},
    )
    assert response.status_code == 400
