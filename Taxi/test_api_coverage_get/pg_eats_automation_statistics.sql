INSERT INTO eats_automation_statistics.api_coverage(
    service_name, coverage_ratio, commit_id, repository, created_at
) VALUES
    ('some-service-1', 0.73, '05ad4efa', 'uservices', now()),
    ('some-service-2', 1.0, '05ad4efa', 'backend-py3', now());
