INSERT INTO etag_data.states(
    driver_id_id,
    valid_since,
    data,
    is_sequence_start
) VALUES (
    IdId('driverSS', '1488'),
    '2019-10-14T18:18:46.540859',
    '
    {
      "state": {
        "status": "no_state"
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
        }
      }
    }
    ',
    True
);
