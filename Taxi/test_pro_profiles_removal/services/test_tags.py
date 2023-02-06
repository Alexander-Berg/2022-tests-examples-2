from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.services import tags as tags_service


async def test_assign_tags(cron_context: context.Context, mockserver):
    @mockserver.json_handler('/tags/v1/assign')
    async def _v1_assign(request: http.Request):
        assert request.headers['X-Idempotency-Token'] == 'idempotency_token'
        assert request.json['provider'] == 'pro-profiles-removal'
        assert request.json['entities'] == [
            {
                'name': 'park_id_contractor_profile_id',
                'type': 'dbid_uuid',
                'tags': {'dbid_uuid_tag': {}},
            },
        ]
        return mockserver.make_response(
            json={'code': '200', 'message': '200'}, status=200,
        )

    entities = tags_service.TagsByEntityType(
        park_contractor=[
            tags_service.ParkContractorProfileTag(
                name='dbid_uuid_tag',
                ttl=None,
                until=None,
                park_id='park_id',
                contractor_profile_id='contractor_profile_id',
            ),
        ],
    )

    await cron_context.services.tags.assign_tags(
        idempotency_token='idempotency_token', entities=entities,
    )
