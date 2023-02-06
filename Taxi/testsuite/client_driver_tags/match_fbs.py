from typing import Any
from typing import Dict

# pylint: disable=import-error
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import DriverTags
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import Request
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import Response
import flatbuffers


def unpack_profiles_fbs_request(data: str) -> Dict[str, Any]:
    root = Request.Request.GetRootAsRequest(data, 0)
    drivers = []
    topics = []
    for i in range(root.DriversLength()):
        driver = root.Drivers(i)
        drivers.append(
            {
                'dbid': driver.Dbid().decode('utf-8'),
                'uuid': driver.Uuid().decode('utf-8'),
            },
        )
    for i in range(root.TopicsLength()):
        topic = root.Topics(i)
        topics.append(topic.decode('utf-8'))
    json = {'drivers': drivers}
    if topics:
        json['topics'] = topics
    return json


def pack_profiles_fbs_response(response_json: Dict[str, Any]) -> str:
    builder = flatbuffers.Builder(0)

    drivers_tags = response_json['drivers']
    fbs_drivers = []
    for driver_tags in drivers_tags:
        fbs_dbid = builder.CreateString(driver_tags['dbid'])
        fbs_uuid = builder.CreateString(driver_tags['uuid'])

        fbs_udid = 0
        udid = driver_tags.get('udid')
        if udid is not None:
            fbs_udid = builder.CreateString(udid)

        fbs_tags = [builder.CreateString(tag) for tag in driver_tags['tags']]
        DriverTags.DriverTagsStartTagsVector(builder, len(fbs_tags))
        for fbs_tag in reversed(fbs_tags):
            builder.PrependUOffsetTRelative(fbs_tag)
        fbs_tags = builder.EndVector(len(fbs_tags))

        DriverTags.DriverTagsStart(builder)
        DriverTags.DriverTagsAddDbid(builder, fbs_dbid)
        DriverTags.DriverTagsAddUuid(builder, fbs_uuid)
        DriverTags.DriverTagsAddTags(builder, fbs_tags)
        DriverTags.DriverTagsAddUdid(builder, fbs_udid)
        fbs_drivers.append(DriverTags.DriverTagsEnd(builder))

    Response.ResponseStartDriversVector(builder, len(fbs_drivers))
    for fbs_driver in reversed(fbs_drivers):
        builder.PrependUOffsetTRelative(fbs_driver)
    fbs_drivers = builder.EndVector(len(fbs_drivers))

    Response.ResponseStart(builder)
    Response.ResponseAddDrivers(builder, fbs_drivers)
    response_fbs = Response.ResponseEnd(builder)
    builder.Finish(response_fbs)
    return builder.Output()
