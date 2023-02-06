INSERT INTO cache.orders_recalc
    (recalc_id, apply_time, author, order_id, params, results)
VALUES
    (
     '777',
     null,
     'an_author',
     '00000000000000000000000000000001',
     '{
      "driver": {
        "backend_variables": {},
        "base_price": {
          "boarding": 100.0,
          "distance": 10.0,
          "time": 1.0,
          "total": 111.0
        },
        "modifications": [
          1
        ],
        "trip_details": {
          "total_distance": 1500.0,
          "total_time": 600,
          "user_options": {},
          "waiting_in_destination_time": 0,
          "waiting_in_transit_time": 0,
          "waiting_time": 0
        }
      },
      "user": {
        "backend_variables": {},
        "base_price": {
          "boarding": 100.0,
          "distance": 10.0,
          "time": 1.0,
          "total": 111.0
        },
        "modifications": [
          2
        ],
        "trip_details": {
          "total_distance": 1500.0,
          "total_time": 600,
          "user_options": {},
          "waiting_in_destination_time": 0,
          "waiting_in_transit_time": 0,
          "waiting_time": 0
        }
      }
    }',
     '{
      "driver": {
        "base_price": {
          "boarding": 100.0,
          "distance": 10.0,
          "time": 1.0,
          "total": 111.0
        },
        "metadata": {},
        "modifications": [
          {
            "delta": {
              "boarding": 0.0,
              "destination_waiting": 0.0,
              "distance": 0.0,
              "requirements": 0.0,
              "time": 0.0,
              "transit_waiting": 0.0,
              "waiting": 0.0
            },
            "id": 1,
            "price": {
              "boarding": 100.0,
              "destination_waiting": 0.0,
              "distance": 10.0,
              "requirements": 0.0,
              "time": 1.0,
              "transit_waiting": 0.0,
              "waiting": 0.0
            },
            "total_delta": 0.0,
            "total_price": 111.0
          }
        ],
        "total_price": 111.0,
        "trip_details": {
          "distance": 1500.0,
          "time": 600.0
        },
        "zones": []
      },
      "user": {
        "base_price": {
          "boarding": 100.0,
          "distance": 10.0,
          "time": 1.0,
          "total": 111.0
        },
        "metadata": {},
        "modifications": [
          {
            "delta": {
              "boarding": 100.0,
              "destination_waiting": 0.0,
              "distance": 10.0,
              "requirements": 0.0,
              "time": 1.0,
              "transit_waiting": 0.0,
              "waiting": 0.0
            },
            "id": 2,
            "price": {
              "boarding": 200.0,
              "destination_waiting": 0.0,
              "distance": 20.0,
              "requirements": 0.0,
              "time": 2.0,
              "transit_waiting": 0.0,
              "waiting": 0.0
            },
            "total_delta": 111.0,
            "total_price": 222.0
          }
        ],
        "total_price": 222.0,
        "trip_details": {
          "distance": 1500,
          "time": 600
        },
        "zones": []
      }
    }'
    );
