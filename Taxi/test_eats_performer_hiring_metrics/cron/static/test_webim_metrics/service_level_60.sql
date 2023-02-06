INSERT INTO webim_chats(
    id,
    created_at,
    updated_at,
    operator_response_time
)
VALUES
   (0, '2022-02-01T10:05:00Z', NOW(), '5 minutes'),  -- too old
   (2, '2022-02-01T11:05:00Z', NOW(), '5 minutes'),  -- good
   (1, '2022-02-01T11:05:00Z', NOW(), '14 minutes 59 seconds'),  -- still good
   (3, '2022-02-01T11:05:00Z', NOW(), '0 seconds'),  -- very good
   (4, '2022-02-01T11:05:00Z', NOW(), '20 minutes'),  -- too slow
   (5, '2022-02-01T11:05:00Z', NOW(), null)  -- not answered yet
