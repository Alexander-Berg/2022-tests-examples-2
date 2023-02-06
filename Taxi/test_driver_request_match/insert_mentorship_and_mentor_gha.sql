REPLACE INTO mentorships (id, country_id, created_at, newbie_unique_driver_id, newbie_park_driver_profile_id, status)
    VALUES
    ('10', 'rus', CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), 'nudid2', 'p2_d2', 'created');
REPLACE INTO mentors
(
  id,
  city,
  country_id,
  country_name_ru,
  db_id,
  driver_uuid,
  first_name,
  last_name,
  phone,
  unique_driver_id,
  updated_at,
  status
  )
VALUES
(
  1,
  "Аккра",
  "gha",
  "Гана",
  "95e091c97677489daa395b605213f75b",
  "733d2ec6a0de4c5285a6b2dc5a0184bf",
  "Tim",
  "Igumenov_uptodate",
  "+78005553535_id",
  "627e38852dfb6348dd9aa37d",
  CAST("2022-07-06T14:59:55.000000Z" AS Timestamp),
  "active"
);
