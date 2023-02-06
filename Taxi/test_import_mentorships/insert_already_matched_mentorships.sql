REPLACE INTO mentorships
(id, country_id, created_at, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, newbie_unique_driver_id, newbie_park_driver_profile_id, status, original_connected_dttm, newbie_last_read_at, mentor_last_read_at)
VALUES
(
  "1",
  "rus",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  "5c91f663d0be228bce70fe727",
  "e7d892bc186c4be8836ba6173c746532_e49e1f62e55941b0813df09ea9d38380",
  "+79930053093_id",
  "Павел",
  "6064c7f28fe28d5ce4f2f8cf",
  "431b2fa719494cceb1dc3b2c35a346ff_c92063fa946c4e4da94b4ab67e20b694",
  "matched",
  CAST("2021-10-31T11:20:00.000000Z" AS Timestamp),
  null,
  null
)
