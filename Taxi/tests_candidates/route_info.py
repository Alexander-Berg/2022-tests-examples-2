# pylint: disable=import-error
import infraver_router.models.detail.RouteInfos as RouteInfos
import infraver_router.models.detail.RouteInfo as RouteInfo
import infraver_router.models.detail.RouterType as RouterType
import flatbuffers
import lz4
import datetime


def timestamp(now):
    return (now - datetime.datetime(1970, 1, 1)) / datetime.timedelta(
        seconds=1,
    )


def fbs_route_infos(geohash, now):
    builder = flatbuffers.Builder(0)

    geohash = builder.CreateString(geohash)
    RouteInfo.RouteInfoStart(builder)
    RouteInfo.RouteInfoAddGeohash(builder, geohash)
    RouteInfo.RouteInfoAddType(builder, RouterType.RouterType.Pedestrian)
    RouteInfo.RouteInfoAddTime(builder, 10)
    RouteInfo.RouteInfoAddDistance(builder, 20)
    RouteInfo.RouteInfoAddCreated(builder, int(timestamp(now)))
    RouteInfo.RouteInfoAddTollRoads(builder, False)
    RouteInfo.RouteInfoAddDeadJam(builder, False)
    RouteInfo.RouteInfoAddCreated(builder, False)

    info = RouteInfo.RouteInfoEnd(builder)
    infos = [info]

    RouteInfos.RouteInfosStartInfosVector(builder, 1)
    builder.PrependUOffsetTRelative(info)
    infos = builder.EndVector(1)
    RouteInfos.RouteInfosStart(builder)
    RouteInfos.RouteInfosAddInfos(builder, infos)
    obj = RouteInfos.RouteInfosEnd(builder)
    builder.Finish(obj)
    return lz4.compress(bytes(builder.Output()))


# hack for flap tests
async def _publish(redis_store, channel, message, callback):
    for _ in range(5):
        redis_store.publish(channel, message)
    await callback.wait_call(2)


async def publish(taxi_candidates, geohash, redis_store, testpoint, now):
    @testpoint('router_cache')
    def router_cache(data):
        pass

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    message = fbs_route_infos(geohash, now)
    await _publish(redis_store, 'channel:route_info', message, router_cache)


def unpack_route_infos(message):
    result = []
    data = lz4.decompress(message)
    fb_root = RouteInfos.RouteInfos.GetRootAsRouteInfos(data, 0)
    for i in range(0, fb_root.InfosLength()):
        info = fb_root.Infos(i)
        result.append(
            {
                'time': info.Time(),
                'distance': info.Distance(),
                'type': info.Type(),
                'geohash': info.Geohash(),
            },
        )
    return result
