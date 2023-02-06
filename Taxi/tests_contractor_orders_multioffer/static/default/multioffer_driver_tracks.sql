INSERT INTO multioffer.multioffers (id, order_id)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'order_id');

INSERT INTO multioffer.multioffers (id, order_id)
    VALUES ('71234567-89ab-cdef-0123-456789abcdef', 'order_id_no_candidates');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, enriched_json)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'win'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', TRUE,
'{
  "clid": "123456789001",
  "dbid": "7f74df331eb04ad78bc2ff25ff88a8f2",
  "uuid": "4bb5a0018d9641c681c1a854b21ec9ab",
  "car_number": "Н123УТ777",
  "name": "Иванов Иван Иванович",
  "tags": [
    "some_tag"
  ],
  "classes": [
    "econom"
  ],
  "route_info": {
    "time": 225,
    "distance": 1935,
    "properties": {
      "toll_roads": false
    },
    "approximate": false
  },
  "chain_info": {
    "order_id": "7835cd0325ab2f2dabf7933e2d680a25",
    "left_dist": 767,
    "left_time": 129,
    "destination": [
      48.5748790393024,
      54.38051404037958
    ]
  },
  "position": [77.89571, 44.12392],
  "adjusted_point": {
    "lat": 44.12392, 
    "lon": 77.89571, 
    "speed": 0, 
    "direction": 23, 
    "timestamp": 1627274239
  }
}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, enriched_json)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 0, 'alias_id2', '{}', TRUE,
'{
  "clid": "123456789002",
  "dbid": "a3608f8f7ee84e0b9c21862beef7e48d",
  "uuid": "e26e1734d70b46edabe993f515eda54e",
  "car_number": "Н321УТ777",
  "name": "Смирнов Смирн Смирнович",
  "route_info": {
    "time": 123,
    "distance": 1000
  },
  "position": [77.89500, 44.12300]
}');
