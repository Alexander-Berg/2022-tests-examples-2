# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821

import yandex.maps.proto.driving.matrix_pb2 as ProtoMatrix
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary


def proto_driving_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


def proto_matrix(data):
    response = ProtoMatrix.Matrix()
    for elem in data:
        row = response.row.add()
        item = row.element.add()
        item.summary.weight.time.value = elem['time']
        item.summary.weight.time.text = ''
        item.summary.weight.time_with_traffic.value = elem['time']
        item.summary.weight.time_with_traffic.text = ''
        item.summary.weight.distance.value = elem['distance']
        item.summary.weight.distance.text = ''

    return response.SerializeToString()


def proto_driving_summary_time_distance(time, distance):
    return proto_driving_summary({'time': time, 'distance': distance})
