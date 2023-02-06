# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821

import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


def proto_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def proto_summary_time_distance(time, distance):
    return proto_summary({'time': time, 'distance': distance})


# TODO: add proto_matrix
