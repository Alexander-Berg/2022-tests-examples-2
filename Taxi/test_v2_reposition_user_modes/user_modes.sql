INSERT INTO etag_data.modes
  (driver_id_id, valid_since, data, is_sequence_start)
VALUES
  (
    IdId('driverSS', '1488'),
    '2017-10-14T12:00:00.000000+00',
    '
    {
      "District": {
        "type": "in_area",
        "start_screen_text": {
          "title": "{\"tanker_key\": \"my_district\"}",
          "subtitle": "{\"tanker_key\": \"my_district\"}"
        },
        "start_screen_subtitle": "{\"tanker_key\": \"my_district\"}",
        "tutorial_body": "{\"tanker_key\": \"my_district\"}",
        "restrictions": [
        ],
        "client_attributes": {},
		"permitted_work_modes": ["orders"],
        "ready_panel": {
          "title": "{\"tanker_key\": \"my_district\"}",
          "subtitle": "{\"tanker_key\": \"my_district\"}"
        },
        "min_allowed_radius": 1,
        "max_allowed_radius": 10,
        "highlighted_radius": 5
      },
      "home": {
        "type": "single_point",
        "start_screen_text": {
          "title": "{\"tanker_key\": \"home\"}",
          "subtitle": "{'
          ' \"tanker_key\": \"home\",'
          ' \"has_limitation\": true,'
          ' \"day_limit\": 1,'
          ' \"week_limit\": 7'
          '}"
        },
        "start_screen_subtitle": "{'
        ' \"tanker_key\": \"home\",'
        ' \"has_limitation\": true,'
        ' \"day_limit\": 1,'
        ' \"week_limit\": 7'
        '}",
        "tutorial_body": "{'
        ' \"tanker_key\": \"home\",'
        ' \"has_limitation\": true,'
        ' \"day_limit\": 1,'
        ' \"week_limit\": 7'
        '}",
        "restrictions": [
        ],
        "client_attributes": {},
		"permitted_work_modes": ["orders"],
        "ready_panel": {
          "title": "{\"tanker_key\": \"home\"}",
          "subtitle": "{\"tanker_key\": \"home\"}"
        },
        "submodes_info": {
          "submodes": {
            "fast": {
               "name": "{'
               '  \"mode_tanker_key\": \"home\",'
               '  \"tanker_key\": \"fast\"'
               '}",'
               '"subname": "{'
               '  \"mode_tanker_key\": \"home\",'
               '  \"tanker_key\": \"fast\"'
               '}",
               "order": 1,
               "restrictions": []
            }
          },
          "highlighted_submode_id": "fast"
        },
        "address_change_alert_dialog": {
          "title": "{\"tanker_key\": \"home\"}",
          "body": "{'
          '  \"tanker_key\": \"home\",'
          '  \"days\": 7'
          '}"
        },
        "address_change_forbidden_dialog": {
          "title": "{\"tanker_key\": \"home\"}",
          "body": "{'
          '  \"tanker_key\": \"home\",'
          '  \"next_change_date\": \"2017-10-14T14:00:00.000000+00\"'
          '}"
        },
        "change_allowed": false,
        "location": {
          "name": "some point",
          "is_valid": true,
          "location": {
            "id": "dapoint",
            "type": "point",
            "point": [3, 4],
            "address": {
              "title": "some address",
              "subtitle": "some city"
            }
          }
        }
      },
      "poi": {
        "type": "free_point",
        "start_screen_text": {
          "title": "{\"tanker_key\": \"poi\"}",
          "subtitle": "{\"tanker_key\": \"poi\", \"is_limitless\": true}"
        },
        "start_screen_subtitle": "{\"tanker_key\": \"poi\", \"is_limitless\": true}",
        "tutorial_body": "{\"tanker_key\": \"poi\"}",
        "restrictions": [
            {
              "image_id": "star",
              "short_text": "{\"tanker_key\": \"poi.restrictions.move\"}",
              "text": "{\"tanker_key\": \"poi.restrictions.move\"}",
              "title": "{\"tanker_key\": \"poi.restrictions.move\"}"
            }
        ],
        "client_attributes": {},
		"permitted_work_modes": ["orders"],
        "ready_panel": {
          "title": "{\"tanker_key\": \"poi\"}",
          "subtitle": "{\"tanker_key\": \"poi\"}"
        },
        "locations": {
          "dapoint": {
            "name": "some point",
            "is_valid": true,
            "location": {
              "id": "dapoint",
              "type": "point",
              "point": [3, 4],
              "address": {
                "title": "some address",
                "subtitle": "some city"
              }
            }
          },
          "dapoint2": {
            "name": "some point2",
            "is_valid": true,
            "location": {
              "id": "dapoint2",
              "type": "point",
              "point": [3, 4],
              "address": {
                "title": "some address",
                "subtitle": "some city"
              }
            }
          }
        }
      }
    }
    ',
    True
);
