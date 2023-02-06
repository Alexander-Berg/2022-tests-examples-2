# pylint: disable=wrong-import-order, import-error
import flatbuffers
import headers.search_bulk.detail.Request as FbsRequest
import headers.search_bulk.detail.Response as FbsResponse
import headers.search_bulk.detail.SearchParam as FbsSearchParam  # noqa: E501
import models.detail.DriverStatus as FbsDriverStatus
import models.detail.TransportType as FbsTransportType
import models.geometry.detail.Viewport as FbsViewport
import pytest


def encode_driver_status(name):
    return {
        'offline': FbsDriverStatus.DriverStatus.Offline,
        'free': FbsDriverStatus.DriverStatus.Free,
        'on-order': FbsDriverStatus.DriverStatus.OnOrder,
        'busy': FbsDriverStatus.DriverStatus.Busy,
    }[name]


def decode_driver_status(status):
    return {
        FbsDriverStatus.DriverStatus.Offline: 'offline',
        FbsDriverStatus.DriverStatus.Free: 'free',
        FbsDriverStatus.DriverStatus.OnOrder: 'on-order',
        FbsDriverStatus.DriverStatus.Busy: 'busy',
    }[status]


def decode_transport_type(transport_type):
    return {
        FbsTransportType.TransportType.Car: 'car',
        FbsTransportType.TransportType.Pedestrian: 'pedestrian',
        FbsTransportType.TransportType.Bicycle: 'bicycle',
        FbsTransportType.TransportType.ElectricBicycle: 'electric-bicycle',
        FbsTransportType.TransportType.Motorcycle: 'motorcycle',
    }[transport_type]


def to_int(val):
    return int(val * 1000000)


def make_headers():
    return {'Content-Type': 'application/x-flatbuffers'}


def create_request(*params):
    builder = flatbuffers.Builder(0)

    params_fbs = []
    for param in params:
        allowed_classes_fbs = [
            builder.CreateString(cl) for cl in param['allowed_classes']
        ]

        FbsSearchParam.SearchParamStartAllowedClassesVector(
            builder, len(allowed_classes_fbs),
        )
        for allowed_class_fbs in allowed_classes_fbs:
            builder.PrependUOffsetTRelative(allowed_class_fbs)
        allowed_classes_fbs = builder.EndVector(len(allowed_classes_fbs))

        statuses_fbs = [encode_driver_status(st) for st in param['statuses']]
        FbsSearchParam.SearchParamStartStatusesVector(
            builder, len(statuses_fbs),
        )
        for status_fbs in statuses_fbs:
            builder.PrependUint16(status_fbs)
        statuses_fbs = builder.EndVector(len(statuses_fbs))

        FbsSearchParam.SearchParamStart(builder)
        FbsSearchParam.SearchParamAddSearchId(builder, param['search_id'])
        FbsSearchParam.SearchParamAddViewport(
            builder,
            FbsViewport.CreateViewport(
                builder,
                to_int(param['tl'][0]),
                to_int(param['tl'][1]),
                to_int(param['br'][0]),
                to_int(param['br'][1]),
            ),
        )
        FbsSearchParam.SearchParamAddAllowedClasses(
            builder, allowed_classes_fbs,
        )
        FbsSearchParam.SearchParamAddStatuses(builder, statuses_fbs)
        params_fbs.append(FbsSearchParam.SearchParamEnd(builder))

    FbsRequest.RequestStartParamsVector(builder, len(params_fbs))
    for param_fbs in params_fbs:
        builder.PrependUOffsetTRelative(param_fbs)
    params_fbs = builder.EndVector(len(params_fbs))

    FbsRequest.RequestStart(builder)
    FbsRequest.RequestAddParams(builder, params_fbs)
    request_fbs = FbsRequest.RequestEnd(builder)

    builder.Finish(request_fbs)
    return builder.Output()


def parse_response(data):
    results = []
    response = FbsResponse.Response.GetRootAsResponse(data, 0)
    for i in range(0, response.ResultsLength()):
        search_result = response.Results(i)

        drivers = []
        for j in range(0, search_result.DriversLength()):
            driver = search_result.Drivers(j)
            # incorrect import on Driver
            # position = driver.Position()
            classes = [
                driver.Classes(k).decode('utf-8')
                for k in range(0, driver.ClassesLength())
            ]
            drivers.append(
                {
                    'dbid': driver.Dbid().decode('utf-8'),
                    'uuid': driver.Uuid().decode('utf-8'),
                    # 'position': {
                    #     'lon': position.Lon() * .000001,
                    #     'lat': position.Lat() * .000001,
                    #     'timestamp': position.Timestamp(),
                    #     'direction': position.Direction(),
                    #     'speed': position.Speed(),
                    #     'source': position.Source(),
                    #     'accuracy': position.Accuracy(),
                    # },
                    'classes': classes,
                    'status': decode_driver_status(driver.Status()),
                    'transport_type': decode_transport_type(
                        driver.TransportType(),
                    ),
                },
            )

        results.append(
            {'search_id': search_result.SearchId(), 'drivers': drivers},
        )
    return results


async def test_bad_request(taxi_candidates):
    response = await taxi_candidates.post(
        'search-bulk', headers=make_headers(), data='request_body',
    )

    assert response.status_code == 400


async def test_empty_request(taxi_candidates):
    response = await taxi_candidates.post(
        'search-bulk', headers=make_headers(), data=create_request(),
    )

    assert response.status_code == 400


async def test_correct_request(taxi_candidates):
    request_body = create_request(
        {
            'search_id': 14,
            'tl': [37.62, 55.75],
            'br': [37.62, 55.75],
            'allowed_classes': ['econom'],
            'statuses': ['free', 'busy'],
        },
    )

    response = await taxi_candidates.post(
        'search-bulk', headers=make_headers(), data=request_body,
    )

    assert response.status_code == 200
    results = parse_response(response.content)
    assert len(results) == 1
    assert results[0]['search_id'] == 14
    assert results[0]['drivers'] == []


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_multisearch(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.559667, 55.685688]},
        ],
    )

    request_body = create_request(
        {
            'search_id': 0,
            'tl': [37.308020, 55.903174],
            'br': [37.921881, 55.565338],
            'allowed_classes': ['econom', 'vip'],
            'statuses': ['free', 'busy'],
        },
        {
            'search_id': 1,
            'tl': [37.680516, 55.787962],
            'br': [37.680518, 55.787964],
            'allowed_classes': ['econom', 'vip'],
            'statuses': ['free', 'busy'],
        },
    )

    response = await taxi_candidates.post(
        'search-bulk', headers=make_headers(), data=request_body,
    )
    assert response.status_code == 200
    results = parse_response(response.content)
    assert len(results) == 2
    results.sort(key=lambda x: x['search_id'])
    for result in results:
        result['drivers'].sort(key=lambda x: x['uuid'])

    assert results == [
        {
            'search_id': 0,
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'status': 'free',
                    'transport_type': 'car',
                },
                {
                    'classes': ['vip'],
                    'dbid': 'dbid0',
                    'uuid': 'uuid1',
                    'status': 'free',
                    'transport_type': 'car',
                },
            ],
        },
        {
            'search_id': 1,
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'status': 'free',
                    'transport_type': 'car',
                },
            ],
        },
    ]
