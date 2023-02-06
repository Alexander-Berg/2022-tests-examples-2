import asyncio
from unittest.mock import AsyncMock, patch

import aiodns
import pytest

from noc.traffic.dns.safedns.dnsl3r.dnsl3r import models, querier

TEST_QUERY_HOST = "host.test"
TEST_QUERY_TIMEOUT = 0.5
TEST_QUERY_RR_TYPE = "AAAA"
TEST_QUERY_RESOLVER_IP = "::1"


async def just_sleep(*args):
    await asyncio.sleep(TEST_QUERY_TIMEOUT + 0.5)


@pytest.mark.asyncio
async def test_query_dns_0_to_1():
    amock = AsyncMock()
    counter = models.Counter(name="192.0.2.1")
    exec_time = await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 1
    assert not counter.status
    assert exec_time > 0
    assert exec_time < TEST_QUERY_TIMEOUT


@pytest.mark.asyncio
async def test_query_dns_0_to_2():
    amock = AsyncMock()
    counter = models.Counter(name="192.0.2.1")
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 2
    assert counter.status


@pytest.mark.asyncio
async def test_query_dns_0_to_0():
    amock = AsyncMock()
    amock.query.side_effect = aiodns.error.DNSError
    counter = models.Counter(name="192.0.2.1")
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 0
    assert not counter.status


@pytest.mark.asyncio
async def test_query_dns_2_to_1():
    amock = AsyncMock()
    amock.query.side_effect = aiodns.error.DNSError
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 1
    assert counter.status


@pytest.mark.asyncio
async def test_query_dns_2_to_0():
    amock = AsyncMock()
    amock.query.side_effect = aiodns.error.DNSError
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 0
    assert not counter.status


@pytest.mark.asyncio
async def test_query_dns_2_to_2():
    amock = AsyncMock()
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 2
    assert counter.status


@pytest.mark.asyncio
async def test_query_dns_2_to_1_and_back():
    amock = AsyncMock()
    amock.query.side_effect = aiodns.error.DNSError
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 1
    assert counter.status
    amock = AsyncMock()
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 2
    assert counter.status


@pytest.mark.asyncio
async def test_query_dns_0_to_1_and_back():
    amock = AsyncMock()
    counter = models.Counter(name="192.0.2.1")
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 1
    assert not counter.status
    amock = AsyncMock()
    amock.query.side_effect = aiodns.error.DNSError
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 0
    assert not counter.status


@pytest.mark.asyncio
async def test_query_dns_timeout():
    amock = AsyncMock()
    amock.query = just_sleep
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 1
    assert counter.status


@pytest.mark.asyncio
async def test_query_dns_double_timeout():
    amock = AsyncMock()
    amock.query = just_sleep
    counter = models.Counter(name="192.0.2.1")
    counter.counter = 2
    counter.status = True
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    await querier._query_dns(counter, TEST_QUERY_HOST, TEST_QUERY_RR_TYPE, TEST_QUERY_TIMEOUT, amock)
    assert counter.counter == 0
    assert not counter.status


@pytest.mark.asyncio
async def test_query_dns_self_dn():
    query_mock = AsyncMock()
    resolver_mock = AsyncMock()
    counter = models.Counter(name="192.0.2.1")
    patcher1 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.querier.socket.gethostname", return_value="selfhost.test")
    patcher2 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.querier._query_dns", new=query_mock)
    patcher3 = patch("noc.traffic.dns.safedns.dnsl3r.dnsl3r.querier.aiodns.DNSResolver", return_value=resolver_mock)
    patcher1.start()
    patcher2.start()
    patcher3.start()
    await querier.query_dns(
        counter,
        "2001:db8:ffff::1",
        {"query_dn": "$self", "query_period": 0.1, "query_timeout": 0.05, "rr_type": "AAAA", "dns_proto": None},
        oneshot=True,
    )
    patcher1.stop()
    patcher2.stop()
    patcher3.stop()
    query_mock.assert_called_with(counter, "selfhost.test", "AAAA", 0.05, resolver_mock)
