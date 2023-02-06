# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821

import yandex.maps.proto.driving_matrix.matrix_pb2 as ProtoMatrix


def proto_matrix(data):
    response = ProtoMatrix.Matrix()
    for elem in data:
        row = response.row.add()
        item = row.element.add()
        item.summary.duration.value = elem['time']
        item.summary.duration.text = ''
        item.summary.distance.value = elem['distance']
        item.summary.distance.text = ''

    return response.SerializeToString()
