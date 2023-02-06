INSERT INTO discounts_operation_calculations.calc_segment_stats_tasks (
    id,
    suggest_id,
    params,
    created_by,
    status,
    result,
    error,
    created_at,
    updated_at
) VALUES
(
    'a8d1e267b27949558980b157ac8e8d76',
    1,
    '{
      "suggest_id": 1,
      "x_yandex_login": "test_user"
    }',
    'test_user',
    'COMPLETED',
    '{
      "currency_code": "RUB",
      "currency_rate": 1.0,
      "segments": {
        "kt": [
          "2",
          "3"
        ]
      },
      "smooth_threshold": 50.0,
      "spark_jobs_meta": [
        {
          "code": "FINISHED",
          "message": "Job successfully finished!",
          "submission_id": "random_submission_id"
        }
      ]
    }',
    '{}',
    '2021-02-02 10:00:00',
    '2021-02-03 10:00:00'
)
;
