INSERT INTO
  changes_0 (
    park_id,
    id,
    date,
    object_id,
    object_type,
    user_id,
    user_name,
    counts,
    values,
    ip
  )
VALUES
  (
    'park_valid1',
    'id1',
    '2020-08-04 11:05:04.879623',
    'group_valid1',
    'Taximeter.Core.Models.Group',
    'author_valid1',
    'Author 1',
    2,
    '{"IsSuper":{"current":"\"False\"","old":""},"Name":{"current":"\"Group\"","old":""}}',
    '2a02:6b8:0:40c:140e:7467:16d2:36'
  ),
  (
    'park_valid1',
    'id2',
    '2020-08-05 11:05:04.879623',
    'group_valid1',
    'Taximeter.Core.Models.Group',
    'author_valid2',
    'Author 2',
    1,
    '{"Name":{"current":"\"NewGroupName\"","old":"\"OldGroupName\""}}',
    '2a02:6b8:0:40c:140e:7467:16d2:36'
  ),
  (
    'park_valid2',
    'id3',
    '2020-08-06 11:05:04.879623',
    'group_valid2',
    'Taximeter.Core.Models.Group',
    'author_valid3',
    'Author 3',
    1,
    '{"Name":{"current":"\"NewName\"","old":"\"OldName\""}}',
    '2a02:6b8:0:40c:140e:7467:16d2:36'
  ),
  (
    'park_valid2',
    'id4',
    '2020-08-06 11:05:04.879623',
    'group_valid2',
    'Taximeter.Core.Models.Group',
    'author_valid3',
    'Author 3',
    1,
    '{"Grants":{"old":"{\"driver_scoring_buy\":\"False\"}","current":"{\"driver_scoring_buy\":\"True\"}"}}',
    '2a02:6b8:0:40c:140e:7467:16d2:36'
  )
;
