SELECT uid, login, password, locked_until, delete_at
FROM user_table
WHERE user_table.uid IN (
  SELECT uid
  FROM (
         SELECT uid, tag
         FROM user_tags_table
                JOIN tag_table USING (tag_id)
         WHERE tag_table.tag IN ('a', 'b', 'c')) uids_with_tags
  GROUP BY uid
  HAVING count(DISTINCT tag) = 3
);

