INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested,
 predefined_comment_ids, order_nr, comment_status)
VALUES
    (11, 'Previously filled feedback', 5, 2, 5, '2021-02-12 12:23', FALSE, '{1,3}', '100000-100011', 'raw'),
    (22, 'Previously filled feedback', 5, 2, 2, '2021-02-12 12:23', FALSE, '{1,3}', '100000-100022', 'raw'),
    (33, 'Previously filled feedback', 5, 2, 3, '2021-02-12 12:23', FALSE, '{1,3}', '100000-100033', 'raw'),
    (44, 'Previously filled feedback', 5, 2, 1, '2021-02-12 12:23', FALSE, '{1,3}', '100000-100044', 'raw');
