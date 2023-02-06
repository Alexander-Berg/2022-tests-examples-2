INSERT INTO dashboards.configs_upload (
    job_idempotency_key,
    status,
    vendor,
    content,
    filepath
)
VALUES (
    'key1', 'applied', 'arcadia', 'content1', 'filepath1'
), (
    null, 'waiting', 'arcadia', 'content4', 'filepath4'
), (
    'key2', 'waiting', 'arcadia', 'content2', 'filepath2'
), (
    'key2', 'waiting', 'arcadia', 'content3', 'filepath3'
), (
    'key4', 'applying', 'arcadia', 'content5', 'filepath5'
), (
    'key4', 'applying', 'arcadia', 'content6', 'filepath6'
);
