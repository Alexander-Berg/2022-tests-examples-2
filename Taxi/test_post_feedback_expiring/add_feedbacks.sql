INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested,
 predefined_comment_ids, order_nr, comment_status)
VALUES
    (10201, 'Previously filled feedback', 5, 2, 5, '2021-02-13T11:23:00+00:00', FALSE, '{1,3}', '106', 'raw'),
    (10202, 'Previously filled feedback', 5, 2, 5, '2021-02-13T11:23:00+00:00', FALSE, '{1,3}', '107', 'raw');
