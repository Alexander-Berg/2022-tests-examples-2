INSERT INTO state.drivers (
    taxi_driver_id,
    yandex_drive_id,
    key_id,
    tag_id,
    issue_state
) VALUES
    (('db2', 'uuid2')::db.taxi_driver_id, 'drive_id1', 'some_key', 'some_tag', 'issued')
;
