import pytest
import elasticsearch


@pytest.mark.skip(reason='elastic ping always returns False after recent client update in contrib (r9618364)')
@pytest.mark.asyncio
async def test_ping(elastic_client: elasticsearch.Elasticsearch):
    assert elastic_client.ping()
