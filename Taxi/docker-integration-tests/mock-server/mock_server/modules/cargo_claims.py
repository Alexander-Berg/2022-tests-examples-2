import datetime
import time
import typing

from aiohttp import web


class ClaimRequest:
    def __init__(
            self,
            claim_id,
            items,
            route_points,
            status,
            revision,
            cursor,
            order_nr=None,
    ):
        self.claim_id: str = claim_id
        self.items: typing.List = items
        self.route_points: typing.List = route_points
        self.status: str = status
        self.revision: int = revision
        self.cursor: str = cursor
        self.order_nr: typing.Optional[str] = order_nr

    def update_cargo_status(self):
        if self.status == 'new':
            self.status = 'ready_for_approval'
            self.revision += 1
        elif self.status == 'ready_for_approval':
            self.status = 'accepted'
            self.revision += 1
        elif self.status == 'accepted':
            self.status = 'performer_found'
            self.revision += 1
        elif self.status == 'performer_found':
            # don't move status before /mark_order_as_delivered call
            self.status = 'performer_found'
        elif self.status == 'delivered':
            # don't move status forward
            self.status = 'delivered'
        else:
            self.status = 'performer_found'
            self.revision += 1


class Application(web.Application):
    def __init__(self):
        super().__init__()

        self.claim_requests: typing.List[ClaimRequest] = []
        self.performers_for_users: typing.List = []

        self.router.add_post(
            '/b2b/cargo/integration/v2/claims/create', self.claims_create,
        )
        self.router.add_post(
            '/b2b/cargo/integration/v1/claims/journal', self.claims_journal,
        )
        self.router.add_post(
            '/b2b/cargo/integration/v1/claims/accept', self.claims_accept,
        )
        self.router.add_post(
            '/b2b/cargo/integration/v2/claims/info', self.claims_info,
        )
        self.router.add_get(
            '/internal/external-performer', self.external_performer,
        )
        self.router.add_get(
            '/b2b/cargo/integration/v1/claims/performer-position',
            self.performer_position,
        )

        # service endpoints
        self.router.add_post('/add_performer', self.add_performer)
        self.router.add_post(
            '/mark_order_as_delivered', self.mark_order_as_delivered,
        )

    def _get_current_claim(
            self, claim_id: str,
    ) -> typing.Optional[ClaimRequest]:
        current_claim: typing.Optional[ClaimRequest] = None
        for claim in self.claim_requests:
            if claim.claim_id == claim_id:
                current_claim = claim
        return current_claim

    @staticmethod
    def _transform_route_point(route_point: typing.Dict, current_time: str):
        route_point['id'] = route_point['point_id']
        del route_point['point_id']
        route_point['visit_status'] = 'pending'
        route_point['visited_at'] = {
            'expected': current_time,
            'actual': current_time,
        }
        return route_point

    async def add_performer(self, request):
        json_data = await request.json()
        # user_phone_number, yandex_uid, courier_id, name, legal_name
        self.performers_for_users.append(json_data)
        return web.json_response({})

    async def mark_order_as_delivered(self, request):
        json_data = await request.json()

        for claim in self.claim_requests:
            if claim.order_nr == json_data['order_nr']:
                claim.status = 'delivered'
                claim.revision += 1
                break
        return web.json_response({})

    async def claims_create(self, request):
        json_data = await request.json()
        current_datetime: str = datetime.datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%S+00:00',
        )

        route_points: typing.List = [
            Application._transform_route_point(route_point, current_datetime)
            for route_point in json_data['route_points']
        ]

        request_id: str = request.query['request_id']
        order_nr: str = '-'.join(request_id.split('-')[:-1])

        new_claim_request: ClaimRequest = ClaimRequest(
            claim_id=f'eats-test-claim-{order_nr}',
            order_nr=order_nr,
            items=json_data['items'],
            route_points=route_points,
            status='new',
            revision=1,
            cursor=f'test_cursor_{order_nr}',
        )
        self.claim_requests.append(new_claim_request)

        eater_user_phone = json_data['route_points'][1]['contact']['phone']
        yandex_uid = ''
        for record in self.performers_for_users:
            if record['user_phone'] == eater_user_phone:
                yandex_uid = record['yandex_uid']
                record['claim_id'] = new_claim_request.claim_id

        return web.json_response(
            {
                'id': new_claim_request.claim_id,
                'corp_client_id': 'test',
                'yandex_uid': yandex_uid,
                'items': new_claim_request.items,
                'route_points': new_claim_request.route_points,
                'status': new_claim_request.status,
                'version': 1,
                'created_ts': current_datetime,
                'updated_ts': current_datetime,
                'revision': new_claim_request.revision,
            },
        )

    async def claims_journal(self, request):
        if not self.claim_requests:
            return web.HTTPInternalServerError
        last_claim = self.claim_requests[-1]

        for claim in self.claim_requests:
            claim.update_cargo_status()

        events = [
            {
                'operation_id': 1,
                'claim_id': current_claim.claim_id,
                'change_type': 'status_changed',
                'updated_ts': datetime.datetime.utcnow().strftime(
                    '%Y-%m-%dT%H:%M:%S+00:00',
                ),
                'revision': current_claim.revision,
                'new_status': current_claim.status,
            }
            for current_claim in self.claim_requests
        ]
        return web.json_response(
            {'cursor': last_claim.cursor, 'events': events},
        )

    @staticmethod
    async def claims_accept(request):
        params: typing.Dict = request.query
        claim_id = params['claim_id']
        return web.json_response(
            {
                'id': claim_id,
                'status': 'accepted',
                'version': 1,
                'taxi_order_id': f'taxi_order_id_{claim_id}',
            },
        )

    async def claims_info(self, request):
        claim_id: str = request.query['claim_id']
        current_claim = self._get_current_claim(claim_id)

        if not current_claim:
            return web.json_response({})

        return web.json_response(
            {
                'id': current_claim.claim_id,
                'items': current_claim.items,
                'route_points': current_claim.route_points,
                'status': 'accepted',
                'version': 1,
                'created_ts': datetime.datetime.utcnow().strftime(
                    '%Y-%m-%dT%H:%M:%S+00:00',
                ),
                'updated_ts': datetime.datetime.utcnow().strftime(
                    '%Y-%m-%dT%H:%M:%S+00:00',
                ),
                'revision': current_claim.revision,
            },
        )

    async def external_performer(self, request):
        params: typing.Dict = request.query
        claim_id = params['claim_id']

        current = {}
        for record in self.performers_for_users:
            if record.get('claim_id') == claim_id:
                current = record
        if not current:
            return web.HTTPInternalServerError
        return web.json_response(
            {
                'eats_profile_id': current['courier_id'],
                'name': current['name'],
                'legal_name': current['legal_name'],
            },
        )

    async def performer_position(self, request):
        claim_id: str = request.query['claim_id']
        current_claim = self._get_current_claim(claim_id)

        if not current_claim:
            return web.json_response({})

        route_point = current_claim.route_points[0]
        coordinates = route_point['address']['coordinates']
        return web.json_response(
            {
                'position': {
                    'lat': coordinates[0],
                    'lon': coordinates[1],
                    'timestamp': int(time.time()),
                },
            },
        )
