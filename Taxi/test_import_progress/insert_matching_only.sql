-- noinspection SqlNoDataSourceInspectionForFile
REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "1",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "5beacb420e9d63004ae80db1",
  "mentorpid1",
  "phone_pd_id",
  "Vasiliy Petrovich",
  "61713503ae03f059f308141c",
  "newbiepid1",
  "matched",
  null,
  null,
  null
);

REPLACE INTO status_transitions
(id, created_at, mentorship_id, from, to)
VALUES
(
  "1",
  CAST("2021-10-1T11:20:00.000000Z" AS Timestamp),
  "1",
  null,
  "matched"
);
