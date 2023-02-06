from clowny_balancer.lib.models import namespace


async def test_fetch_many_by_ns_ids(web_context):
    awacs_ns_ids = ['ns1', 'ns2']
    async with web_context.pg.secondary.acquire() as conn:
        namespaces = await namespace.Namespace.fetch_many(
            web_context, conn, awacs_namespace_ids=awacs_ns_ids,
        )
        assert len(namespaces) == 2
