INSERT INTO multioffer.multioffers (id, order_id, lookup_request, settings)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'order_id_5',
'{
  "zone_id": "togliatti",
  "lookup": {"generation": 1, "version": 1, "wave": 1},
  "callback": {"url": "some_url", "timeout_ms": 500, "attempts": 2},
  "order": {"nearest_zone": "moscow"}
}',
'{
  "dispatch_type": "test_dispatch"
}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, enriched_json)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', TRUE,
'{
  "tags": [
    "some_tag"
  ],
  "classes": [
    "econom"
  ],
  "unique_driver_id": "60c9ccf18fe28d5ce431ce88",
  "license_id": "318fb895466a4cd599486ada5c5c0ffa",
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
  }
}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, enriched_json)
    VALUES ('51234567-89ab-cdef-0123-456789abcdef', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 10, 'alias_id2', '{}', FALSE,
'{
  "tags": [
    "some_tag"
  ],
  "classes": [
    "econom"
  ],
  "unique_driver_id": "60c9ccf18fe28d5ce431ce88",
  "license_id": "318fb895466a4cd599486ada5c5c0ffa",
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
  }
}');

