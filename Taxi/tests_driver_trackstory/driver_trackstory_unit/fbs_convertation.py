# pylint: disable=import-error
from driver_trackstory.fbs import Response


def convert_position_to_local_repr(gps_position):
    return {
        'timestamp': int(gps_position.Timestamp()),
        'lon': float(gps_position.Lon()),
        'lat': float(gps_position.Lat()),
        'speed': float(gps_position.Speed()),
        'direction': int(gps_position.Direction()),
        'accuracy': float(gps_position.Accuracy()),
    }


def convert_fbs_to_local_repr(fbs_bin_string):
    root = Response.Response.GetRootAsResponse(fbs_bin_string, 0)
    assert root.DataLength() > 0
    result = {}
    # convert to our representation
    for i in range(root.DataLength()):
        data = root.Data(i)
        driver_data = {'raw': [], 'adjusted': [], 'alternatives': []}
        for j in range(data.RawLength()):
            raw = data.Raw(j)
            driver_data['raw'].append(convert_position_to_local_repr(raw))
        for j in range(data.AdjustedLength()):
            adj = data.Adjusted(j)
            driver_data['adjusted'].append(convert_position_to_local_repr(adj))
        for j in range(data.AlternativesLength()):
            alts = data.Alternatives(j)
            alts_list = []
            for k in range(alts.AlternativesLength()):
                alt = alts.Alternatives(k)
                alts_list.append(convert_position_to_local_repr(alt))
            driver_data['alternatives'].append(alts_list)
        result[data.DriverId().decode('ascii')] = driver_data
    return result
