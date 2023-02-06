-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO rescue.application
    (park_id, driver_profile_id, order_id, longtitude, latitude, st_ticket)
VALUES
    ('db1', 'uuid1', 'order_with_application1', 68.9, 56.89, 'TICKET-1');

INSERT INTO rescue.media
    (order_id, media_id, attach_id, content_type)
VALUES
    ('order_with_application1', 'media1', 'attach1', 'some_content_type');

INSERT INTO rescue.media
    (order_id, media_id, attach_id, content_type)
VALUES
    ('order_with_application1', 'media2', 'attach2', 'some_content_type');

INSERT INTO rescue.media
    (order_id, media_id, attach_id, content_type)
VALUES
    ('order_with_application1', 'media3', 'attach3', 'some_content_type');
