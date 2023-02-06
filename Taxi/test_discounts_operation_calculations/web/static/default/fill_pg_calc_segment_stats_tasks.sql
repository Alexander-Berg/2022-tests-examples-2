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
) VALUES (
    'a8d1e267b27949558980b157ac8e8d73',
    1,
    '{
        "suggest_id": 1,
        "x_yandex_login": "test_user"
    }',
    'test_user',
    'CREATED',
    '{"segments": {"kt1": ["0", "1", "2", "3", "control", "random"]}, "spark_jobs_meta": [{"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131740-4878"}, {"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131756-4879"}], "smooth_threshold": 50.0}',
    '{}',
    '2021-02-02 10:00:00',
    '2021-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d74',
    2,
    '{
        "suggest_id": 2,
        "x_yandex_login": "test_user"
    }',
    'test_user',
    'CREATED',
    '{"segments": {"kt1": ["0", "1", "2", "3", "control", "random"]}, "spark_jobs_meta": [{"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131740-4879"}, {"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131756-4880"}], "smooth_threshold": 50.0}',
    '{}',
    '2021-02-02 10:00:00',
    '2021-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d75',
    3,
    '{
        "suggest_id": 3,
        "x_yandex_login": "test_user"
    }',
    'test_user',
    'CREATED',
    '{"segments": {"kt1": ["0", "1", "2", "3", "control", "random"]}, "spark_jobs_meta": [{"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131740-4879"}, {"code": "FINISHED", "message": "Job successfully finished!", "submission_id": "driver-20220207131756-4880"}], "smooth_threshold": 50.0}',
    '{}',
    '2021-02-02 10:00:00',
    '2021-02-03 10:00:00'
),
(
    'a8d1e267b27949558980b157ac8e8d76',
    7,
    '{
      "suggest_id": 7,
      "x_yandex_login": "test_user"
    }',
    'test_user',
    'COMPLETED',
    '{
      "currency_code": null,
      "currency_rate": 1.0,
      "segments": {
        "kt": [
          "control",
          "metrika_active_Hconv",
          "metrika_active_Lconv",
          "metrika_active_Mconv",
          "metrika_notactive_Hconv",
          "metrika_notactive_Lconv",
          "metrika_notactive_Mconv",
          "random"
        ],
        "kt1": [
          "control",
          "metrika_active_Hconv",
          "metrika_active_Lconv",
          "metrika_active_Mconv",
          "metrika_notactive_Hconv",
          "metrika_notactive_Lconv",
          "metrika_notactive_Mconv",
          "random"
        ]
      },
      "smooth_threshold": 50.0,
      "spark_jobs_meta": [
        {
          "code": "FINISHED",
          "message": "Job successfully finished!",
          "submission_id": "random_submission_id"
        },
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
