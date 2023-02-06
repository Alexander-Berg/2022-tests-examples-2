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
  ( 'passport', 'puid1', 'market-courier', 'PHONE_PD_ID', 'TRACK_ID', FALSE),
  ( 'passport', 'puid2', 'market-courier', NULL, NULL, FALSE),
  ( 'passport', 'puid3', 'market-courier', 'PHONE_PD_ID3', NULL, TRUE),
  ( 'passport', 'puid4', 'market-courier', 'PHONE_PD_ID4', NULL, FALSE)
;


INSERT INTO se.ownpark_profile_forms_common
  (
    phone_pd_id,
    state,
    external_id
  )
VALUES
  ( 'PHONE_PD_ID3', 'INITIAL', 'external_id1' )
;
