# pylint: disable=import-error
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import Driver
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import Request
from fbs.driver_tags.handlers.v1_drivers_match_profiles_fbs import Response
import flatbuffers


def pack_profiles_fbs_request(request_json):
    builder = flatbuffers.Builder(0)

    topics = request_json['topics'] if 'topics' in request_json else []
    fbs_topics = [builder.CreateString(topic) for topic in topics]
    Request.RequestStartTopicsVector(builder, len(fbs_topics))
    for fbs_topic in reversed(fbs_topics):
        builder.PrependUOffsetTRelative(fbs_topic)
    fbs_topics = builder.EndVector(len(fbs_topics))

    drivers = request_json['drivers'] if 'drivers' in request_json else []
    fbs_drivers = []
    for driver in drivers:
        fbs_dbid = builder.CreateString(driver['dbid'])
        fbs_uuid = builder.CreateString(driver['uuid'])
        Driver.DriverStart(builder)
        Driver.DriverAddDbid(builder, fbs_dbid)
        Driver.DriverAddUuid(builder, fbs_uuid)
        fbs_drivers.append(Driver.DriverEnd(builder))

    Request.RequestStartDriversVector(builder, len(fbs_drivers))
    for fbs_driver in reversed(fbs_drivers):
        builder.PrependUOffsetTRelative(fbs_driver)
    fbs_drivers = builder.EndVector(len(fbs_drivers))

    Request.RequestStart(builder)
    Request.RequestAddDrivers(builder, fbs_drivers)
    Request.RequestAddTopics(builder, fbs_topics)
    request_fbs = Request.RequestEnd(builder)
    builder.Finish(request_fbs)
    return builder.Output()


def unpack_profiles_fbs_response(data):
    root = Response.Response.GetRootAsResponse(data, 0)
    driver_tags = []
    for i in range(root.DriversLength()):
        driver = root.Drivers(i)
        tags = [
            driver.Tags(j).decode('utf-8') for j in range(driver.TagsLength())
        ]

        item = {
            'dbid': driver.Dbid().decode('utf-8'),
            'uuid': driver.Uuid().decode('utf-8'),
            'tags': tags,
        }
        if driver.Udid() is not None:
            item['udid'] = driver.Udid().decode('utf-8')

        driver_tags.append(item)
    return {'drivers': driver_tags}
