INSERT INTO pro_profiles_removal.requests(id, state, phone_pd_id, created_at)
VALUES
('67677feefc2f43ca9939b2e74f094d29','canceled','7ad36bc7560449998acbe2c57a75c293_110982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('77677feefc2f43ca9939b2e74f094d29','pending','7ad36bc7560449998acbe2c57a75c293_110982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('87677feefc2f43ca9939b2e74f094d29','created','7ad36bc7560449998acbe2c57a75c293_120982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('2e6c83a30e7c40589516ea8437007988','created','7ad36bc7560449998acbe2c57a75c293_120982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('13f9329afd534daa96de907d1444fb97','pending','7ad36bc7560449998acbe2c57a75c293_130982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('3e6c83a30e7c40589516ea8437007988','cancel_requested','7ad36bc7560449998acbe2c57a75c293_140982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'),
('23f9329afd534daa96de907d1444fb97','pending','7ad36bc7560449998acbe2c57a75c293_130982b584844dfcab07f29adf9661ab_phone_pd_id','2022-01-01T12:00:00+0000'); -- pre inserted row for test_cancel_new_one_cancels_all

INSERT INTO pro_profiles_removal.profiles(request_id, park_id, contractor_profile_id)
VALUES
('67677feefc2f43ca9939b2e74f094d29','7ad36bc7560449998acbe2c57a75c293','110982b584844dfcab07f29adf9661ab'),
('77677feefc2f43ca9939b2e74f094d29','7ad36bc7560449998acbe2c57a75c293','110982b584844dfcab07f29adf9661ab'),
('87677feefc2f43ca9939b2e74f094d29','7ad36bc7560449998acbe2c57a75c293','110982b584844dfcab07f29adf9661ab'),
('2e6c83a30e7c40589516ea8437007988','7ad36bc7560449998acbe2c57a75c293','120982b584844dfcab07f29adf9661ab'),
('13f9329afd534daa96de907d1444fb97','7ad36bc7560449998acbe2c57a75c293','130982b584844dfcab07f29adf9661ab'),
('3e6c83a30e7c40589516ea8437007988','7ad36bc7560449998acbe2c57a75c293','140982b584844dfcab07f29adf9661ab'),
('23f9329afd534daa96de907d1444fb97','7ad36bc7560449998acbe2c57a75c293','160982b584844dfcab07f29adf9661ab'); -- pre inserted row for test_cancel_new_one_cancels_all