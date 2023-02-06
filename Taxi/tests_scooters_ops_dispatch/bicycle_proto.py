# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821

import yandex.maps.proto.driving_matrix.matrix_pb2 as ProtoCarMatrix
import yandex.maps.proto.bicycle_matrix.matrix_pb2 as ProtoBicycleMatrix
import yandex.maps.proto.bicycle.summary_pb2 as ProtoBicycleSummary


def proto_bicycle_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoBicycleSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    return response.SerializeToString()


def proto_car_matrix(data, row_size, col_size):
    response = ProtoCarMatrix.Matrix()
    for i in range(0, row_size):
        row = response.row.add()
        for j in range(0, col_size):
            item = row.element.add()
            item.summary.duration.value = data[j + i * col_size]['time']
            item.summary.duration.text = ''
            item.summary.distance.value = data[i * col_size]['distance']
            item.summary.distance.text = ''

    return response.SerializeToString()


def proto_bicycle_matrix(data, row_size, col_size):
    response = ProtoBicycleMatrix.Matrix()
    for i in range(0, row_size):
        row = response.row.add()
        for j in range(0, col_size):
            item = row.element.add()
            item.summary.weight.time.value = data[j + i * col_size]['time']
            item.summary.weight.time.text = ''
            item.summary.weight.distance.value = data[i * col_size]['distance']
            item.summary.weight.distance.text = ''
    return response.SerializeToString()


def proto_bicycle_summary_time_distance(time, distance):
    return proto_bicycle_summary({'time': time, 'distance': distance})
