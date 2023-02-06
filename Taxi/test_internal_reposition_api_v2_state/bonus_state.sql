INSERT INTO etag_data.states
  (driver_id_id, valid_since, data, is_sequence_start)
VALUES
  (
  IdId('uuid', 'dbid777'),
  '2017-10-14T18:18:46.540859',
  '
  {
    "state": {
      "state_id": "who am i",
      "status": "bonus",
      "bonus": {
        "session_id": "some_session_id",
        "mode_id": "SuperSurge",
        "submode_id": "SuperSuperSurge",
        "expires_at": "2017-10-14T18:19:46.540859+00",
        "started_at": "2017-10-14T18:18:46.540859+00",
        "icon_id": "icon",
        "headline": {
          "title": "{\"mode_tanker_key\": \"home\", \"tanker_key\": \"bonus_translation\"}",
          "subtitle": "{\"mode_tanker_key\": \"home\", \"tanker_key\": \"bonus_translation\"}"
        },
        "subline": {
          "title": "{\"mode_tanker_key\": \"home\", \"tanker_key\": \"bonus_translation\"}",
          "subtitle": "{\"mode_tanker_key\": \"home\", \"tanker_key\": \"bonus_translation\"}"
        },
        "client_attributes": {"dead10cc": "deadbeef"}
      }
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
          "title": "{\"tanker_key\": \"my_district\", \"period\": \"week\", \"used_duration\": 90, \"limit_duration\": 120}"
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
