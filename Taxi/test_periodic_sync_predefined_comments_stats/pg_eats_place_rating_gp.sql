insert into eda_cdm_supply.v_fct_place_predefined_comment_count_act
(
    place_id,
    predefined_comment,
    predefined_comment_cnt,
    predefined_comment_type,
    rating_dt)
VALUES
  (
     1, 'predefined comment 1', 4, 'dislike', '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1, 'predefined comment 1', 4, 'dislike', '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1, 'predefined comment 1', 5, 'like', '2021-06-30 00:03:30+00'::timestamp - interval '1 day'
  ),
  (
     2, 'predefined comment 2', 6, 'like', current_date
  ),
  (
     2, 'predefined comment 2', 5, 'dislike', current_date - interval '1 day'
  ),
  (
     2, 'predefined comment 21', 7, 'dislike', current_date - interval '2 day'
  ),
  (
     4, 'predefined comment 4', 11, 'like', current_date
  ),
  (
     4, 'predefined comment 4', 10, 'like', current_date - interval '1 day'
  ),
  (
     1, 'predefined comment 1', 3, 'like', '2021-06-30 00:03:30+00'::timestamp - interval '2 day'
  );
