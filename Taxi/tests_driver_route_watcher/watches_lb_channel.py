import tests_driver_route_watcher.points_list_fbs as PointlistFbs


class WatchesLbChannel:
    def __init__(self, lb_handle):
        self.lb_handle = lb_handle

    async def send(self, data):
        return await self.lb_handle.send_json(
            consumer='watch_commands', data=data,
        )

    async def start_watch(
            self,
            driver_id,
            destination,
            service_id='',
            metainfo=None,
            destinations=None,
            order_id=None,
            transport_type='car',
            toll_roads=False,
            timestamp=None,
            nearest_zone=None,
            country=None,
    ):
        points = destinations
        if points is None or not points:
            points = PointlistFbs.to_point_list([destination], compact=True)
        data = {
            'driver_dbid': driver_id['dbid'],
            'driver_uuid': driver_id['uuid'],
            'internal': {
                'destination': {
                    'full_destinations': points,
                    'service_id': service_id,
                    'transport_type': transport_type,
                },
                'operation': 'start',
            },
        }
        out_destination = data['internal']['destination']
        if order_id is not None:
            out_destination['order_id'] = order_id
        if metainfo is not None:
            out_destination['metainfo'] = metainfo
        if country is not None:
            out_destination['country'] = country
        if nearest_zone is not None:
            out_destination['zone'] = nearest_zone
        if toll_roads:
            out_destination['user_chose_toll_road'] = toll_roads
        import json
        print(json.dumps(data))
        return await self.send(data)

    async def stop_watch(self, driver_id, destination, service_id=''):
        destinations = [destination]
        if isinstance(destination[0], list):
            # if destiantion contains multiple points
            destinations = destination

        data = {
            'driver_dbid': driver_id['dbid'],
            'driver_uuid': driver_id['uuid'],
            'internal': {
                'destination': {
                    'full_destinations': PointlistFbs.to_point_list(
                        destinations, compact=True,
                    ),
                    'service_id': service_id,
                },
                'operation': 'stop',
            },
            'reset': True,
        }
        return await self.send(data)

    async def stop_watch_by_orders(self, driver_id, orders, service_id=''):
        data = {
            'driver_dbid': driver_id['dbid'],
            'driver_uuid': driver_id['uuid'],
            'internal': {
                'destination': {
                    'full_destinations': [],
                    'service_id': service_id,
                    'inactive_orders': orders,
                },
                'operation': 'stop_by_orders',
            },
            'reset': True,
        }
        return await self.send(data)

    async def stop_watch_all(self, driver_id, service_id):
        data = {
            'driver_dbid': driver_id['dbid'],
            'driver_uuid': driver_id['uuid'],
            'internal': {
                'destination': {
                    'full_destinations': [],
                    'service_id': service_id,
                },
                'operation': 'stop_by_orders',
            },
        }
        return await self.send(data)

    async def start_watch_old(
            self,
            driver_id,
            destination,
            service_id,
            order_id=None,
            meta='',
            taxi_status=None,
    ):
        data = {
            'driver_uuid': driver_id['uuid'],
            'driver_dbid': driver_id['dbid'],
            'service_id': service_id,
            'metainfo': meta,
        }
        if order_id is not None:
            data.update({'order_id': order_id})

        if service_id == 'processing:transporting':
            data.update(
                {
                    'field': 'destinations',
                    'destinations': [destination],
                    'destinations_statuses': [],
                    'taxi_status': 'transporting',
                },
            )
        elif service_id == 'processing:driving':
            data.update(
                {
                    'field': 'source',
                    'source': destination,
                    'taxi_status': 'driving',
                },
            )
        else:
            data.update({'field': 'source', 'source': destination})

        if taxi_status is not None:
            data.update({'taxi_status': taxi_status})

        return await self.send(data)

    async def stop_watch_old(self, driver_id, destinations, service_id):
        data = {
            'driver_uuid': driver_id['uuid'],
            'driver_dbid': driver_id['dbid'],
            'service_id': service_id,
            'reset': True,
        }

        if service_id == 'processing':
            data.update(
                {
                    'field': 'all',
                    'source': destinations[0],
                    'destinations': destinations[1:],
                    'destinations_statuses': [],
                },
            )
        else:
            data.update({'field': 'source', 'source': destinations[0]})

        return await self.send(data)
