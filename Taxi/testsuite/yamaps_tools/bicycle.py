# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821

import yandex.maps.proto.bicycle.summary_pb2 as ProtoBicycleSummary


def proto_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoBicycleSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    return response.SerializeToString()


def proto_summary_time_distance(time, distance):
    return proto_summary({'time': time, 'distance': distance})


# TODO: add proto_matrix
