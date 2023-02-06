INSERT INTO crm_admin.audience
VALUES
('Driver', 'Driver'),
('User', 'Users')
;


INSERT INTO crm_admin.quicksegment_schemas (
    audience,
    major_ver,
    minor_ver,
    name,
    format,
    body,
    created_at
)
VALUES
(
    'Driver',
    0,  -- major_ver
    1,  -- minor_ver
    'table_schema',
    'yaml',
    '
---
tables:
  - name: base
    path:

root_table: base

graph: []
    ',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    1,  -- minor_ver
    'filter_schema',
    'yaml',
    '
---
filters:
  - id: main
    where: "true"

targets:
  - main
    ',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    1,  -- minor_ver
    'input_schema',
    'json',
    '{}',
    '2020-11-24 01:00:00'
),

(
    'User',
    0,  -- major_ver
    1,  -- minor_ver
    'table_schema',
    'yaml',
    '
---
tables:
  - name: base
    path:

root_table: base

graph: []
    ',
    '2020-11-24 01:00:00'
),
(
    'User',
    0,  -- major_ver
    1,  -- minor_ver
    'filter_schema',
    'yaml',
    '
---
filters:
  - id: main
    where: "true"

targets:
  - main
    ',
    '2020-11-24 01:00:00'
),
(
    'User',
    0,  -- major_ver
    1,  -- minor_ver
    'input_schema',
    'json',
    '{}',
    '2020-11-24 01:00:00'
);
