from taxi.antifraud.geo_markup.lib import Reducer, distance


def test_reducer_empty():
    r = Reducer([], "", "")
    inp = {
        "gps_latitude": 0.,
        "gps_longitude": 0.,
        "gps_altitude": 0.,
        "gps_precision": 0.,
        "gps_speed": 0.,
        "gps_direction": 0.,
        "timestamp": 0.,
        "Cells_CellsIDs": None,
        "Cells_CountriesCodes": None,
        "Cells_OperatorsIDs": None,
        "Cells_Lacs": None,
        "Wifi_SignalsStrengths": None,
        "Wifi_Macs": None,
    }
    row_groups = [(None, [inp])]
    result = next(r(row_groups))
    assert result["lbs_latitude"] == -1
    assert result["lbs_longitude"] == -1
    assert result["lbs_precision"] == -1
    assert str(result["lbs_found_by"]) == "none"


def test_reducer_same_rows():
    r = Reducer([], "", "")
    inp = [
        {
            "gps_latitude": 0.,
            "gps_longitude": 0.,
            "gps_altitude": 0.,
            "gps_precision": 0.,
            "gps_speed": 0.,
            "gps_direction": 0.,
            "timestamp": 0.,
            "Cells_CellsIDs": None,
            "Cells_CountriesCodes": None,
            "Cells_OperatorsIDs": None,
            "Cells_Lacs": None,
            "Wifi_SignalsStrengths": None,
            "Wifi_Macs": None,
        },
        {
            "gps_latitude": 0.,
            "gps_longitude": 0.,
            "gps_altitude": 0.,
            "gps_precision": 0.,
            "gps_speed": 0.,
            "gps_direction": 0.,
            "timestamp": 0.,
            "Cells_CellsIDs": None,
            "Cells_CountriesCodes": None,
            "Cells_OperatorsIDs": None,
            "Cells_Lacs": None,
            "Wifi_SignalsStrengths": None,
            "Wifi_Macs": None,
        },
        {
            "gps_latitude": 0.,
            "gps_longitude": 0.,
            "gps_altitude": 0.,
            "gps_precision": 0.,
            "gps_speed": 0.,
            "gps_direction": 0.,
            "timestamp": 0.,
            "Cells_CellsIDs": None,
            "Cells_CountriesCodes": None,
            "Cells_OperatorsIDs": None,
            "Cells_Lacs": None,
            "Wifi_SignalsStrengths": None,
            "Wifi_Macs": None,
        },
    ]

    row_groups = [(None, inp)]
    result = list(r(row_groups))
    assert len(result) == 1
    assert result[0]["factors"]["gps_coords_freeze"] is False


def test_reducer_same_coords():
    r = Reducer([], "", "")
    inp = [
        {
            "gps_latitude": 0.,
            "gps_longitude": 0.,
            "gps_altitude": 0.,
            "gps_precision": 0.,
            "gps_speed": 0.,
            "gps_direction": 0.,
            "timestamp": 0.,
            "Cells_CellsIDs": None,
            "Cells_CountriesCodes": None,
            "Cells_OperatorsIDs": None,
            "Cells_Lacs": None,
            "Wifi_SignalsStrengths": None,
            "Wifi_Macs": None,
        },
        {
            "gps_latitude": 0.,
            "gps_longitude": 0.,
            "gps_altitude": 0.,
            "gps_precision": 0.,
            "gps_speed": 0.,
            "gps_direction": 0.,
            "timestamp": 1.,
            "Cells_CellsIDs": None,
            "Cells_CountriesCodes": None,
            "Cells_OperatorsIDs": None,
            "Cells_Lacs": None,
            "Wifi_SignalsStrengths": None,
            "Wifi_Macs": None,
        },
    ]
    row_groups = [(None, inp)]
    result = list(r(row_groups))
    assert len(result) == 2
    assert result[0]["factors"]["gps_coords_freeze"] is True
    assert result[1]["factors"]["gps_coords_freeze"] is True


def test_distance():
    assert distance((0, 0), (0, 0)) == 0
    assert 633000 <= distance((55.7558, 37.6173), (59.9343, 30.3351)) <= 634000  # Москва-Питер
    assert 20000000 <= distance((0, 0), (180, 0)) <= 20100000  # половина экватора
