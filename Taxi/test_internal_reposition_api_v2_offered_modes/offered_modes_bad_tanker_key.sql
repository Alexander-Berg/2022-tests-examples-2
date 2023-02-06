INSERT INTO etag_data.offered_modes
  (driver_id_id, valid_since, data, is_sequence_start)
VALUES
  (
    IdId('driverSS', '1488'),
    '2017-10-14T12:00:00.000000+00',
    '
    {
      "SuperSurge": {
        "restrictions": [
          {
            "image_id": "star",
            "short_text": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}",
            "text": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}",
            "title": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}"
          }
        ],
        "client_attributes": {},
		"permitted_work_modes": ["orders"],
        "ready_panel": {
          "title": "{\"tanker_key\": \"SuperSurge\"}",
          "subtitle": "{\"tanker_key\": \"SuperSurge\"}"
        },
        "locations": {
          "0": {
            "location": {
              "id": "0",
              "type": "point",
              "point": [3.14, 4.20],
              "address": {"title": "", "subtitle": ""}
            },
            "offered_at": "2017-10-14T12:00:00+00",
            "expires_at": "2017-10-15T12:00:00+00",
            "image_id": "image_id_0",
            "description": "Get millions for just getting around",
            "destination_radius": 3.14,
            "restrictions": [
              {
                "image_id": "icon id 1",
                "short_text": "short text 1",
                "text": "text 1",
                "title": "title 1"
              },
              {
                "image_id": "icon id 2",
                "short_text": "short text 2",
                "text": "text 2",
                "title": "title 2"
              }
            ]
          },
          "1": {
            "location": {
              "id": "1",
              "type": "point",
              "point": [4.20, 3.14],
              "address": {"title": "", "subtitle": ""}
            },
            "offered_at": "2017-10-15T12:00:00+00",
            "expires_at": "2017-10-16T12:00:00+00",
            "image_id": "image_id_1",
            "description": "Get nothing for just getting around",
            "destination_radius": 4.20,
            "restrictions": []
          }
        }
      }, 
      "NewSuperSurge": {
        "restrictions": [
          {
            "image_id": "star",
            "short_text": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}",
            "text": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}",
            "title": "{\"tanker_key\": \"SuperSurge.offer.restrictions\"}"
          }
        ],
        "client_attributes": {},
		"permitted_work_modes": ["orders"],
        "ready_panel": {
          "title": "{\"tanker_key\": \"BadKey\"}",
          "subtitle": "{\"tanker_key\": \"BadKey\"}"
        },
        "locations": {
          "0": {
            "location": {
              "id": "0",
              "type": "point",
              "point": [3.14, 4.20],
              "address": {"title": "", "subtitle": ""}
            },
            "offered_at": "2017-10-14T12:00:00+00",
            "expires_at": "2017-10-15T12:00:00+00",
            "image_id": "image_id_0",
            "description": "Get millions for just getting around",
            "destination_radius": 3.14,
            "restrictions": [
              {
                "image_id": "icon id 1",
                "short_text": "short text 1",
                "text": "text 1",
                "title": "title 1"
              },
              {
                "image_id": "icon id 2",
                "short_text": "short text 2",
                "text": "text 2",
                "title": "title 2"
              }
            ]
          },
          "1": {
            "location": {
              "id": "1",
              "type": "point",
              "point": [4.20, 3.14],
              "address": {"title": "", "subtitle": ""}
            },
            "offered_at": "2017-10-15T12:00:00+00",
            "expires_at": "2017-10-16T12:00:00+00",
            "image_id": "image_id_1",
            "description": "Get nothing for just getting around",
            "destination_radius": 4.20,
            "restrictions": []
          }
        }
      }
      
    }
    ',
    True
);
