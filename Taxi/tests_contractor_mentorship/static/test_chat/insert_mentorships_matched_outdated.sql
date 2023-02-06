-- noinspection SqlNoDataSourceInspectionForFile

REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "1",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "mentoruid1",
  "mentorpid1",
  "phone_pd_id",
  "Vasiliy Petrovich",
  "newbieuid1",
  "newbiepid1",
  "matched",
  CAST("2021-11-11T00:00:01.000000Z" AS Timestamp),
  null,
  null
);


REPLACE INTO status_transitions
(id, created_at, mentorship_id, from, to)
VALUES
(
  "1",
  CAST("2021-9-30T11:20:00.000000Z" AS Timestamp),
  "1",
  null,
  "requested"
),
(
  "2",
  CAST("2021-10-1T11:20:00.000000Z" AS Timestamp),
  "1",
  "requested",
  "matched"
);


REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "2",
  "rus",
  CAST("2021-10-10T11:20:00.000000Z" AS Timestamp),
  "mentoruid1",
  "mentorpid1",
  "phone_pd_id",
  "Vasiliy Petrovich",
  "newbieuid2",
  "newbiepid2",
  "matched",
  CAST("2021-10-10T00:00:01.000000Z" AS Timestamp),
  null,
  null
);


REPLACE INTO status_transitions
(id, created_at, mentorship_id, from, to)
VALUES
(
  "1",
  CAST("2021-10-10T11:20:00.000000Z" AS Timestamp),
  "2",
  null,
  "requested"
),
(
  "2",
  CAST("2021-10-11T11:20:00.000000Z" AS Timestamp),
  "2",
  "requested",
  "matched"
);
