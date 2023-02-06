
INSERT INTO coop_accounts.accounts
(
    id,
    type,
    color,
    tz_offset,
    members_number,
    owner_id,
    created_at,
    updated_at,
    is_active,
    revision,
    has_specific_limit,
    has_rides
)
VALUES
(
    'ok_account',
    'family',
    'FFFFFF',
    '+0300',
    1,
    'user1',
    CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP),
    CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP),
    True,
    'revision1',
    True,
    False
),
(
    'ok_account_with_rides',
    'family',
    'FFFFFF',
    '+0300',
    1,
    'user1',
    CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP),
    CAST('2019-01-01 10:00:00.000001' AS TIMESTAMP),
    True,
    'revision1',
    True,
    True
)
;
