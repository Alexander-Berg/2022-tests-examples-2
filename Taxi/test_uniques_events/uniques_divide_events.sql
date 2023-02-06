REPLACE INTO mentorships
(id, newbie_unique_driver_id, newbie_park_driver_profile_id, status, mentor_unique_driver_id, mentor_park_driver_profile_id, mentor_phone_pd_id, mentor_full_name, original_connected_dttm, newbie_last_read_at, mentor_last_read_at, created_at, country_id)
VALUES
("01", "newbie_udid_01", "newbie_dbid_uuid_01", "bad_status_01", "mentor_udid_01", "mentor_dbid_uuid_01", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("02", "newbie_udid_02", "newbie_dbid_uuid_02", "bad_status_02", "mentor_udid_01", "mentor_dbid_uuid_02", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("03", "newbie_udid_03", "newbie_dbid_uuid_03", "created", null, null, null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("04", "newbie_udid_04", "newbie_dbid_uuid_04", "in_progress", "mentor_udid_04", "mentor_dbid_uuid_04", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("05", "newbie_udid_05", "newbie_dbid_uuid_05", "bad_status_03", "mentor_udid_04", "mentor_dbid_uuid_05", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("06", "newbie_udid_06", "newbie_dbid_uuid_06", "in_progress", "mentor_udid_06", "mentor_dbid_uuid_06", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("07", "newbie_udid_07", "newbie_dbid_uuid_07", "failed", "mentor_udid_06", "mentor_dbid_uuid_07", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus"),
("08", "newbie_udid_08", "newbie_dbid_uuid_08", "matched", "mentor_udid_06", "mentor_dbid_uuid_08", null, null, null, null, null, CAST("2021-10-31T11:20:00.000000Z" AS Timestamp), "rus");
