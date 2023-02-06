INSERT INTO etag_data.states
  (driver_id_id, valid_since, data, is_sequence_start)
VALUES
  (
  IdId('uuid', 'dbid777'),
  '2017-10-14T18:18:46.540859',
  '
  {
    "state": {
      "status": "active",
      "session_id": "some_session_id",
      "mode_id": "poi",
      "submode_id": "fast",
      "finish_until": "2017-10-14T19:18:00+00:00",
      "started_at": "2017-10-14T18:18:00+00:00",
      "offer": {
        "offered_at": "2017-10-14T19:18:00+00:00",
        "expires_at": "2017-10-14T18:18:00+00:00",
        "image_id": "image",
        "description": "offer description",
        "destination_radius": 300.0,
        "restrictions": []
      },
      "location": {
        "id": "0",
        "type": "point",
        "point": [3.14, 4.20],
        "address": {"title": "Pushkina, 10", "subtitle": "Moscow"}
      },
      "active_panel": {
        "title": "{\"tanker_key\": \"poi\"}",
        "subtitle": "{\"tanker_key\": \"poi\"}"
      },
      "finish_dialog": {
        "title": "{\"tanker_key\": \"poi\"}",
        "body": "{\"tanker_key\": \"poi\"}"
      },
      "rule_violations": [
        {
          "expires_at": "2018-09-01T08:00:00+00:00",
          "message": {
            "title": "{\"mode_tanker_key\":\"poi\",\"tanker_key\":\"route_warning\"}\n",
            "subtitle": "{\"mode_tanker_key\":\"poi\",\"tanker_key\":\"route_warning\"}\n"
          }
        }
      ],
      "restrictions": [],
      "client_attributes": {}
    },
    "usages": {
      "home": {
        "usage_allowed": true,
        "start_screen_usages": {
          "subtitle": "{\"tanker_key\": \"home\", \"period\": \"day\"}",
          "title": "{\"tanker_key\": \"home\", \"period\": \"day\", \"used_count\": 1, \"limit_count\": 2}"
        },
        "usage_limit_dialog": {
          "title": "{\"tanker_key\": \"home\"}",
          "body": "{\"tanker_key\": \"home\", \"period\": \"day\"}"
        }
      },
      "my_district": {
        "usage_allowed": true,
        "start_screen_usages": {
          "subtitle": "{\"tanker_key\": \"my_district\", \"period\": \"week\"}",
          "title": "{\"tanker_key\": \"my_district\", \"period\": \"week\", \"used_duration\": 30, \"limit_duration\": 60}"
        },
        "usage_limit_dialog": {
          "title": "{\"tanker_key\": \"my_district\"}",
          "body": "{\"tanker_key\": \"my_district\", \"period\": \"week\"}"
        }
      }
    }
  }
  ',
  True
)
;
