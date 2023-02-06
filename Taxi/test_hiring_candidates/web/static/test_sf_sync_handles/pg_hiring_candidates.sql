INSERT INTO hiring_candidates.candidates (
       id,
       personal_phone_id
) VALUES (
       'some_candidate_id',
       'e5551ddc7f45472aba6cb359a124c083'
);

INSERT INTO hiring_candidates.leads (
       lead_id,
       external_id,
       candidate_id,
       created_ts,
       last_name,
       activation_city,
       park_condition_id,
       date_of_birth
) VALUES (
       'to_be_deleted',
       'to_be_deleted_external_id',
       'some_candidate_id',
       '2020-01-01T12:00:00',
       'Po',
       'Activation City',
       'Park Condition',
       '1998-02-02'
),
(
       'to_be_updated',
       'to_be_updated_external_id',
       'some_candidate_id',
       '2020-01-01T12:00:00',
       'To Be Updated',
       'Activation City',
       'Park Condition',
       '1998-02-02'
);

INSERT INTO hiring_candidates.leads (
       lead_id,
       external_id,
       candidate_id,
       created_ts,
       last_name,
       activation_city,
       park_condition_id,
       date_of_birth,
       extra
) VALUES (
       'to_be_updated_extra_fields',
       'to_be_updated_extra_external_id',
       'some_candidate_id',
       '2020-01-01T12:00:00',
       'Daa Daa',
       'Activation City',
       'Park Condition',
       '1998-02-02',
       '{"extra_field_1": "value", "extra_field_2": "old_value", "extra_field_3": ["a", "b"]}'
);
