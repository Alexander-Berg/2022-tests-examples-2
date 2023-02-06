from concurrent import futures

import grpc

from example_service_proto.proto.grc import route_guide_pb2
from example_service_proto.proto.grc import route_guide_pb2_grpc


ROUTE_GUIDE_DB = [
    {
        'location': {'latitude': 407838351, 'longitude': -746143763},
        'name': 'Patriots Path, Mendham, NJ 07945, USA',
    },
    {
        'location': {'latitude': 408122808, 'longitude': -743999179},
        'name': '101 New Jersey 10, Whippany, NJ 07981, USA',
    },
]
PRESENT_POINT = route_guide_pb2.Point(latitude=407838351, longitude=-746143763)
ABSENT_POINT = route_guide_pb2.Point(latitude=0, longitude=0)
SERVER_TIMEOUT = 3


def test_client_server_get_feature():
    server = start_server()

    # Run client
    with grpc.insecure_channel('localhost:9999') as channel:
        stub = route_guide_pb2_grpc.RouteGuideStub(channel)
        present_feature = stub.GetFeature(PRESENT_POINT)
        absent_feature = stub.GetFeature(ABSENT_POINT)

    server.stop(SERVER_TIMEOUT)
    assert present_feature == route_guide_pb2.Feature(
        name='Patriots Path, Mendham, NJ 07945, USA', location=PRESENT_POINT,
    )
    assert absent_feature == route_guide_pb2.Feature(
        name='', location=ABSENT_POINT,
    )


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
        RouteGuideServicer(), server,
    )
    server.add_insecure_port('[::]:9999')
    server.start()
    return server


def read_route_guide_database():
    feature_list = []
    for item in ROUTE_GUIDE_DB:
        feature = route_guide_pb2.Feature(
            name=item['name'],
            location=route_guide_pb2.Point(
                latitude=item['location']['latitude'],
                longitude=item['location']['longitude'],
            ),
        )
        feature_list.append(feature)
    return feature_list


def get_feature(feature_db, point):
    for feature in feature_db:
        if feature.location == point:
            return feature
    return None


class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.db = read_route_guide_database()

    def GetFeature(self, request, context):
        feature = get_feature(self.db, request)
        if feature is None:
            return route_guide_pb2.Feature(name='', location=request)
        return feature
