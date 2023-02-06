INSERT INTO se.ownpark_profile_forms_contractor
  (
    initial_park_id,
    initial_contractor_id,
    profession,
    phone_pd_id,
    track_id,
    is_phone_verified
  )
VALUES
  ( 'passport', 'puid1', 'market-courier', NULL, NULL, FALSE),
  ( 'passport', 'puid2', 'market-courier', 'PHONE_PD_ID', 'OLD_TRACK_ID', FALSE),
  ( 'passport', 'puid3', 'market-courier', 'OTHER_PHONE_PD_ID', 'OLD_TRACK_ID', FALSE),
  ( 'passport', 'puid4', 'market-courier', 'OTHER_PHONE_PD_ID', NULL, TRUE),
  ( 'passport', 'puid5', 'market-courier', 'PHONE_PD_ID', NULL, TRUE)
;

INSERT INTO se.ownpark_profile_forms_common
  (
    phone_pd_id,
    state,
    external_id
  )
VALUES
  ( 'OTHER_PHONE_PD_ID', 'INITIAL', 'external_id1' ),
  ( 'PHONE_PD_ID', 'INITIAL', 'external_id2' )
;
