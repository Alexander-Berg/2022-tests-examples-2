INSERT INTO se.ownpark_profile_forms_contractor
  (
    initial_park_id,
    initial_contractor_id,
    phone_pd_id,
    last_step
  )
VALUES
  ( 'passport', 'puid1', 'phone_pd_id', '' )
;

INSERT INTO se.ownpark_profile_forms_common
  (
    phone_pd_id,
    state,
    initial_park_id,
    initial_contractor_id,
    external_id
  )
VALUES
  ( 'phone_pd_id', 'INITIAL', 'passport', 'puid1', 'external_id' )
;
