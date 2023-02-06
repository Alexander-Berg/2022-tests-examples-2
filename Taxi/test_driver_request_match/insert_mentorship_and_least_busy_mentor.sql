REPLACE INTO mentorships (id, country_id, created_at, newbie_unique_driver_id, newbie_park_driver_profile_id, status)
    VALUES
    ('10', 'rus', CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), 'nudid2', 'p2_d2', 'created');

REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "1",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "unique1",
  "park1_driver1",
  "phone_pd_id",
  "Tim Verybusy",
  "newbieuid1",
  "newbiepid1",
  "matched",
  CAST("2021-11-11T00:00:01.000000Z" AS Timestamp),
  null,
  null
),
(
  "2",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "unique1",
  "park1_driver1",
  "phone_pd_id",
  "Tim Verybusy",
  "newbieuid2",
  "newbiepid2",
  "matched",
  CAST("2021-11-11T00:00:01.000000Z" AS Timestamp),
  null,
  null
),
(
  "3",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "unique2",
  "park1_driver2",
  "phone_pd_id",
  "Tim LeastBusy",
  "newbieuid3",
  "newbiepid3",
  "matched",
  CAST("2021-11-11T00:00:01.000000Z" AS Timestamp),
  null,
  null
);

INSERT INTO mentors
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
  "Москва",
  "rus",
  "Гана",
  "park1",
  "driver1",
  "Tim",
  "VeryBusy",
  "+78005553535_id",
  "unique1",
  CAST("2022-07-06T14:59:55.000000Z" AS Timestamp),
  "active"
),
(
  2,
  "Москва",
  "rus",
  "Гана",
  "park1",
  "driver2",
  "Tim",
  "LeastBusy",
  "+78005553535_id",
  "unique2",
  CAST("2022-07-06T14:59:55.000000Z" AS Timestamp),
  "active"
);
