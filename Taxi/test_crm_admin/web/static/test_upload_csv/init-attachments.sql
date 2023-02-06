INSERT INTO crm_admin.uploaded_csv (
    id,
    campaign_id,
    s3_key,
    yt_path,
    created_at
)
VALUES (
    1,
    1,
    'some-key',
    'some-path',
    now()
);
