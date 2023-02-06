-- noinspection SqlNoDataSourceInspectionForFile

REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "1",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "5a05965fe222fb36506fdc76",
  "mentorpid1",
  "phone_pd_id",
  "Vasiliy Petrovich",
  "5fecc8268fe28d5ce4388d88",
  "newbiepid1",
  "in_progress",
  CAST("2021-11-26T12:00:00.000000Z" AS Timestamp),
  null,
  null
),
(
  "2",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "mentoruid2",
  "mentorpid2",
  "phone_pd_id2",
  "Ne Smog",
  "newbieuid2",
  "newbiepid2",
  "in_progress",
  CAST("1970-01-01T00:00:12.000000Z" AS Timestamp),
  null,
  null
);
