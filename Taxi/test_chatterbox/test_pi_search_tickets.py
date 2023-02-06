import datetime
import random
import string
from typing import List

import pytest

import crm.proto.b2b_pb2 as b2b

from chatterbox.internal.pi import token
from chatterbox.internal.pi import utils


def credentials(partner_ids: List[str]) -> b2b.UserCredentials:
    return b2b.UserCredentials(partner_id=partner_ids)


def search_request(
        partner_ids: List[str], expression: str,
) -> b2b.SearchTicketsRequest:
    return b2b.SearchTicketsRequest(
        credentials=credentials(partner_ids),
        query=b2b.Query(expression=expression),
    )


def search_next_request(
        partner_ids: List[str], page_token: b2b.PageToken,
) -> b2b.SearchTicketsNextRequest:
    return b2b.SearchTicketsNextRequest(
        credentials=credentials(partner_ids), token=page_token,
    )


async def pi_call(chatterbox, endpoint, msg):
    reply = await chatterbox.post(
        f'/v1/pi/{endpoint}',
        data=msg.SerializeToString(),
        headers={'Content-type': 'application/protobuf', 'X-Yandex-UID': '42'},
    )
    return reply


async def pi_search_tickets(
        chatterbox, request, endpoint: str = 'search_tickets',
):
    reply = await pi_call(chatterbox, endpoint, request)
    assert reply.status == 200

    response = b2b.SearchTicketsResponse()
    response.ParseFromString(await reply.read())
    return response


async def pi_search_all(chatterbox, partner_ids: List[str], expr: str = ''):
    request = search_request(partner_ids, expr)
    response = await pi_search_tickets(chatterbox, request)
    pages = [list(response.tickets)]

    while pages[-1]:
        next_request = search_next_request(partner_ids, response.next_page)
        response = await pi_search_tickets(
            chatterbox, next_request, 'search_tickets_next',
        )
        pages.append(list(response.tickets))
    pages.pop()
    return pages


@pytest.mark.parametrize(
    'partner_ids, expected_ticket_ids',
    [
        (['p42'], {'42-archived', '42-waiting'}),
        (['p451'], {'451-c1', '451-c2', '451-c3', '451-w1', '451-w2'}),
        (['p38', 'p42'], {'38a', '38b', '42-archived', '42-waiting'}),
    ],
)
async def test_search__given_empty_query__filters_by_partner_id(
        web_app_client, partner_ids, expected_ticket_ids,
):
    request = search_request(partner_ids, '')

    response = await pi_search_tickets(web_app_client, request)

    ids = {t.ticket_id for t in response.tickets}
    assert ids == expected_ticket_ids


@pytest.mark.parametrize(
    'partner_ids, expected_ticket_ids, query',
    [
        (['p42'], {'42-archived', '42-waiting'}, ' '),
        (
            ['p42'],
            {'42-archived', '42-waiting'},
            """status in ('CLOSED','NEED_INFO')""",
        ),
        (['p42'], {'42-archived'}, """status = 'CLOSED' """),
        (['p42'], {'42-archived'}, """status != 'NEED_INFO' """),
        (['p42'], {'42-waiting'}, """\tstatus \t=   'NEED_INFO' """),
        (['p42'], {'42-waiting'}, """status != 'CLOSED' """),
        (['p42'], {'42-archived', '42-waiting'}, """status != 'OPEN' """),
        (['p38'], set(), """ created < '2015-01-01' """),
        (['p38'], {'38a', '38b'}, """ created > '2015-01-01' """),
        (
            ['p38'],
            {'38a'},
            """ created > '2015-01-01' and created < '2016-01-01' """,
        ),
        (['p38'], set(), """ updated < '2015-01-01' """),
        (['p38'], {'38a', '38b'}, """ updated > '2015-01-01' """),
        (
            ['p38'],
            {'38a'},
            """ updated > '2015-01-01' and updated < '2016-01-01' """,
        ),
        (['p38'], {'38a'}, """details.field_a = 'value A' """),
        (['p38'], {'38b'}, """details.field_b = 'value B' """),
        (['p38'], {'38a', '38b'}, """details.field = 'value' """),
    ],
)
async def test_search_tickets__finds_correct_tickets(
        web_app_client, partner_ids, query, expected_ticket_ids,
):
    request = search_request(partner_ids, query)

    response = await pi_search_tickets(web_app_client, request)

    ids = {t.ticket_id for t in response.tickets}
    assert ids == expected_ticket_ids


async def test_search_tickets__correctly_fills_ticket(web_app_client):
    request = search_request(['p12'], '')
    timestamp = utils.timestamp(datetime.datetime(2018, 6, 7, 12, 34, 56))
    expected_ticket = b2b.Ticket(
        ticket_id='12-single',
        partner_id='p12',
        initial_comment='Please help!',
        status=b2b.Status.STATUS_CLOSED,
        created=timestamp,
        updated=timestamp,
        details={'a': 'b', 'c': '42'},
    )

    response = await pi_search_tickets(web_app_client, request)

    assert len(response.tickets) == 1
    assert response.tickets[0] == expected_ticket


@pytest.mark.parametrize(
    'invalid_query',
    [
        ' x ',
        'status != 1',
        """ status > '2020-10-10' """,
        'order by 4',
        '1 > 2',
        '\'x',
        'created = true',
    ],
)
async def test_search_tickets__given_invalid_query__returns_400(
        web_app_client, invalid_query,
):
    request = search_request(['1'], invalid_query)

    reply = await pi_call(web_app_client, 'search_tickets', request)
    assert reply.status == 400

    assert 'invalid query' in await reply.text()


@pytest.mark.parametrize(
    'partner_ids, expected_id_pages',
    [
        (['unknown'], []),
        (['p42'], [['42-archived', '42-waiting']]),
        (['p451'], [['451-w1', '451-w2', '451-c1', '451-c2', '451-c3']]),
    ],
)
async def test_pagination_with_default_pagesize__orders_by_updated(
        web_app_client, partner_ids, expected_id_pages,
):
    ticket_pages = await pi_search_all(web_app_client, partner_ids, '')
    id_pages = [[t.ticket_id for t in page] for page in ticket_pages]
    assert expected_id_pages == id_pages


@pytest.mark.config(
    CHATTERBOX_MARKET_PARTNER_INTERFACE={'search': {'pagesize': 10}},
)
async def test_pagination_with_pagesize_10__finds_single_page(web_app_client):
    ticket_pages = await pi_search_all(web_app_client, ['p42'], '')
    id_pages = [[t.ticket_id for t in page] for page in ticket_pages]
    assert [['42-archived', '42-waiting']] == id_pages


@pytest.mark.config(
    CHATTERBOX_MARKET_PARTNER_INTERFACE={'search': {'pagesize': 1}},
)
async def test_pagination_with_pagesize_1__finds_several_pages(web_app_client):
    ticket_pages = await pi_search_all(web_app_client, ['p451'], '')
    id_pages = [[t.ticket_id for t in page] for page in ticket_pages]
    assert [
        ['451-w1'],
        ['451-w2'],
        ['451-c1'],
        ['451-c2'],
        ['451-c3'],
    ] == id_pages


def test_kwargs_to_token__is_isomorphic():
    kwargs = {}
    to_kwargs, to_token = token.token_to_kwargs, token.kwargs_to_token

    def random_string(size: int) -> str:
        return ''.join(random.choices(string.ascii_letters, k=size))

    for _ in range(5):
        kwargs[random_string(10)] = random_string(20)
        search_token = to_token(kwargs)

        assert search_token == to_token(to_kwargs(search_token))
        assert kwargs == to_kwargs(to_token(kwargs))
