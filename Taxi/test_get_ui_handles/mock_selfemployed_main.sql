INSERT INTO se.ownpark_profile_forms_contractor
  (
    initial_park_id,
    initial_contractor_id,
    phone_pd_id,
    last_step
  )
VALUES
  ( 'passport', 'puid1', 'PHONE_PD_ID', 'intro' ),
  ( 'passport', 'puid2', 'PHONE_PD_ID2', 'intro' ),
  ( 'passport', 'puid3', 'PHONE_PD_ID3', 'phone-bind' )
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
  ( 'PHONE_PD_ID', 'INITIAL', 'passport', 'puid1', 'external_id1' ),
  ( 'PHONE_PD_ID1', 'INITIAL', 'passport', 'puid2', 'external_id2' ),
  ( 'PHONE_PD_ID2', 'INITIAL', 'passport', 'puid3', 'external_id3' )
;
