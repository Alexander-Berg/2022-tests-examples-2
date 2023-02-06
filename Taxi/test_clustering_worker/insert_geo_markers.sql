INSERT INTO services
    (id, name)
VALUES (1, 'service');

INSERT INTO feeds
    (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z',
        '{"text": "How do you do?", "title": "Hello, Ivan!"}', '2018-12-01T00:00:00.0Z');

INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('a659567e-a916-4546-a8e8-895ea5d2711e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91286527715694, 40.791238746327316), 4326)::geography,
        -111.91286527715694,
        40.791238746327316,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('d8013ccb-52be-45c5-bdd4-ba67a3704b0c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.90335549087736, 40.76243608032395), 4326)::geography,
        -111.90335549087736,
        40.76243608032395,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('95671cb4-5e3b-4e8d-a422-25a3c51853bd',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85847680507557, 40.7017362280835), 4326)::geography,
        -111.85847680507557,
        40.7017362280835,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('33b58ed2-111c-4ad1-afdd-f3a5bb4015bd',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9320636630802, 40.751026017947225), 4326)::geography,
        -111.9320636630802,
        40.751026017947225,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('5cfa13b9-0a52-4081-8fcb-e77ad493623c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.86237103786308, 40.75513670661053), 4326)::geography,
        -111.86237103786308,
        40.75513670661053,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('e59c896f-3718-4c8d-8c1e-9d341b9f288f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88197919330544, 40.75999597468564), 4326)::geography,
        -111.88197919330544,
        40.75999597468564,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('1ccad2f1-299d-499e-8e9c-04e7a12282fc',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.87540425810131, 40.733505967170146), 4326)::geography,
        -111.87540425810131,
        40.733505967170146,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('0866d61b-aa49-4f24-971c-efa4c0b2ac3f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.87337468346563, 40.765408671211), 4326)::geography,
        -111.87337468346563,
        40.765408671211,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('5b0d3428-d186-4c5e-b43d-568a1ea02041',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.92589347788994, 40.797359604335256), 4326)::geography,
        -111.92589347788994,
        40.797359604335256,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('4a886606-0bdb-43f5-8e15-2b2facc95e82',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9066343411228, 40.75418519651928), 4326)::geography,
        -111.9066343411228,
        40.75418519651928,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('0977c634-1b0a-4d00-95a9-b166eeb1da2c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9383103835018, 40.742505281158316), 4326)::geography,
        -111.9383103835018,
        40.742505281158316,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('af61bc56-e8df-4124-98b2-194ba2cf08d8',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9011162495568, 40.73897646220448), 4326)::geography,
        -111.9011162495568,
        40.73897646220448,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('48d3f71d-ec71-43d9-ad7c-9b932d1a933e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.90530327238254, 40.76400210338882), 4326)::geography,
        -111.90530327238254,
        40.76400210338882,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('04199c14-c7fe-4c4f-ad4e-474302171259',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88869231895613, 40.746596299800615), 4326)::geography,
        -111.88869231895613,
        40.746596299800615,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('5b79c865-709f-4e3d-9412-f063d4aa3b3b',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.99388927254464, 40.72623117750962), 4326)::geography,
        -111.99388927254464,
        40.72623117750962,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('32e8d607-f6cd-4ba9-8cfd-4776a2ed9937',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.90422219733436, 40.76492529359981), 4326)::geography,
        -111.90422219733436,
        40.76492529359981,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('2189b2ce-0b05-4e0d-8494-8a8d933ceb7d',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85857258131357, 40.723359045975215), 4326)::geography,
        -111.85857258131357,
        40.723359045975215,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('39059401-d13d-44de-9497-b25510d08e36',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8940415028217, 40.76043105443506), 4326)::geography,
        -111.8940415028217,
        40.76043105443506,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('b4caa44a-cf36-43a1-8842-de082a6b1aec',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91977954771365, 40.76705014057636), 4326)::geography,
        -111.91977954771365,
        40.76705014057636,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('ae2a227d-e82e-4b78-b8b1-1056e30be37d',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91692751288899, 40.75113824088857), 4326)::geography,
        -111.91692751288899,
        40.75113824088857,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('378258ba-422b-4323-8987-ecac91cfe4a3',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89118242760078, 40.764782701434456), 4326)::geography,
        -111.89118242760078,
        40.764782701434456,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('5d8c7767-0d76-46cc-b29f-979612cd70b9',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85410407820228, 40.71808072661205), 4326)::geography,
        -111.85410407820228,
        40.71808072661205,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('97439fb0-767c-4bb7-8e5b-cb89e57ed5f8',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89181174939388, 40.73616701916842), 4326)::geography,
        -111.89181174939388,
        40.73616701916842,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('fcb09ee4-d699-4b24-a20f-385e41b553e9',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89423431609312, 40.77874023374077), 4326)::geography,
        -111.89423431609312,
        40.77874023374077,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('87540299-b965-4c1e-aa72-f585db19bb0e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.90894240234091, 40.76226859279996), 4326)::geography,
        -111.90894240234091,
        40.76226859279996,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('15a3f375-27a6-4a1a-bcd3-5e2945750369',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85969562544456, 40.73858609032154), 4326)::geography,
        -111.85969562544456,
        40.73858609032154,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('8cfbfea4-597b-45bc-bec7-805dd2ac9161',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8654432714941, 40.76063033800117), 4326)::geography,
        -111.8654432714941,
        40.76063033800117,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('15ac1243-d88c-40bd-8759-55acf1205f43',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9383103835018, 40.742505281158316), 4326)::geography,
        -111.9383103835018,
        40.742505281158316,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('635bc8da-68f9-4800-bdff-1652608fff69',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91696812607842, 40.760703408101676), 4326)::geography,
        -111.91696812607842,
        40.760703408101676,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('d815abc2-ed5e-4e95-8d45-139eb85bb4c1',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91860516371649, 40.776246286699674), 4326)::geography,
        -111.91860516371649,
        40.776246286699674,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('999d747c-39a1-466d-9608-a84a0929b32e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91689448608774, 40.73337454065784), 4326)::geography,
        -111.91689448608774,
        40.73337454065784,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('3c97ae27-0f7c-4220-9e60-b18854b80700',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88482672298504, 40.76182565051585), 4326)::geography,
        -111.88482672298504,
        40.76182565051585,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('6ed25279-0c5e-43af-8398-a3bd0c1d2c1c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8881280616292, 40.75017176958587), 4326)::geography,
        -111.8881280616292,
        40.75017176958587,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('ddfa9ad0-9f36-46ad-8c14-7ef2d64b8f0e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85440727129362, 40.72365986090757), 4326)::geography,
        -111.85440727129362,
        40.72365986090757,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('f8157e1b-869d-40b1-aa8c-3b413c1be331',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.93081480950804, 40.74075163303118), 4326)::geography,
        -111.93081480950804,
        40.74075163303118,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('683683d2-656b-4f33-9339-fa4425b8eed2',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.86614551962631, 40.75094483821625), 4326)::geography,
        -111.86614551962631,
        40.75094483821625,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('b87e11b2-228a-44c5-909b-329f35bb4da0',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8522417435379, 40.775066462770795), 4326)::geography,
        -111.8522417435379,
        40.775066462770795,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('d836796d-b327-49db-ac12-f2db4471392f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85480421016098, 40.73545000248629), 4326)::geography,
        -111.85480421016098,
        40.73545000248629,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('573a1c8d-ef33-4fec-b058-d8bdaf0579f2',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.84793301876249, 40.771955825213276), 4326)::geography,
        -111.84793301876249,
        40.771955825213276,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('7e4eb8e8-d14c-4477-bad5-5beaec4a753b',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85380332496634, 40.72685105439292), 4326)::geography,
        -111.85380332496634,
        40.72685105439292,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('695a7eac-d3dd-487f-b710-1d7928e7f3ea',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.87546262037223, 40.722496671139226), 4326)::geography,
        -111.87546262037223,
        40.722496671139226,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('f0182c0b-a2e3-423e-b475-1db022d332ab',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8443690983434, 40.74547173913036), 4326)::geography,
        -111.8443690983434,
        40.74547173913036,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('dc8ff7e7-bf4d-42cd-828b-02f8bc4d0a41',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8931638967945, 40.7484917662599), 4326)::geography,
        -111.8931638967945,
        40.7484917662599,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('41f129e3-a5e9-4309-9875-40475d4cce0f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88299118885081, 40.76150776130867), 4326)::geography,
        -111.88299118885081,
        40.76150776130867,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('c321ae86-51a0-4fc4-8795-96a24f1d10de',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.896255679374, 40.75696529632489), 4326)::geography,
        -111.896255679374,
        40.75696529632489,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('c29e7b91-78c0-4562-b850-4535e9999df8',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.86485264366242, 40.72588136468704), 4326)::geography,
        -111.86485264366242,
        40.72588136468704,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('3efc5feb-8e8f-4978-b48b-3f2d680c1a6b',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.90420240194405, 40.764631679017185), 4326)::geography,
        -111.90420240194405,
        40.764631679017185,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('2c875a12-9347-4e25-abc0-faf7aff16c8b',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88523456105543, 40.728668183687354), 4326)::geography,
        -111.88523456105543,
        40.728668183687354,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('998a6ded-c5c5-4e3f-bdbe-d8958c720ab4',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.81968055886593, 40.73386263398749), 4326)::geography,
        -111.81968055886593,
        40.73386263398749,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('55289b2c-92d2-4177-8042-ab0299d1b9df',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88197919330544, 40.75999597468564), 4326)::geography,
        -111.88197919330544,
        40.75999597468564,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('075b1192-904b-474e-bf76-be7dded0838b',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88770532543738, 40.7304468883352), 4326)::geography,
        -111.88770532543738,
        40.7304468883352,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('72a4bba9-c5bd-485a-9353-68f029d54b0d',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89896983288295, 40.75201565302209), 4326)::geography,
        -111.89896983288295,
        40.75201565302209,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('9442ec0d-b46e-4806-a957-1a80212ea47a',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.95266088662085, 40.774835770400095), 4326)::geography,
        -111.95266088662085,
        40.774835770400095,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('0a721461-414a-4225-b128-6154bc67de34',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88664573674549, 40.76304382621829), 4326)::geography,
        -111.88664573674549,
        40.76304382621829,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('f3dd7dcd-421d-48c7-a3e0-757412c40a66',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.95171102621187, 40.78782724671056), 4326)::geography,
        -111.95171102621187,
        40.78782724671056,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('03921325-2d52-43fd-85f3-687026c4019f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89100292664364, 40.76621053885981), 4326)::geography,
        -111.89100292664364,
        40.76621053885981,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('afd0305d-3dc4-401c-8c8f-615bc6f580de',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89403089279931, 40.73866005086396), 4326)::geography,
        -111.89403089279931,
        40.73866005086396,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('fd45c6d5-dd1d-4060-9258-652cfee57e3c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.94205840221754, 40.751172803243755), 4326)::geography,
        -111.94205840221754,
        40.751172803243755,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('70140a27-a7bb-4341-88f3-97093dcc5d22',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.92611729108809, 40.791007648395464), 4326)::geography,
        -111.92611729108809,
        40.791007648395464,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('2b4b6abb-d6de-4c4f-99f1-af72101deba5',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88772849613156, 40.736416587727774), 4326)::geography,
        -111.88772849613156,
        40.736416587727774,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('4ec77e4a-bab5-4c75-81ec-c1a89a7c8a88',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.95397500632237, 40.83482876921501), 4326)::geography,
        -111.95397500632237,
        40.83482876921501,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('484f0d39-4944-46f8-9281-aeb4e9caf3fe',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88829574544592, 40.73338179901982), 4326)::geography,
        -111.88829574544592,
        40.73338179901982,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('6866195a-e827-4c3b-9811-76c730645aaa',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88485302540299, 40.76073317420627), 4326)::geography,
        -111.88485302540299,
        40.76073317420627,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('aa3da038-6853-435d-baea-12bb429e263a',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89793750627884, 40.7593996656816), 4326)::geography,
        -111.89793750627884,
        40.7593996656816,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('b5cec947-d6b7-46f4-bda4-d730e448d093',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9382685021546, 40.76009081960292), 4326)::geography,
        -111.9382685021546,
        40.76009081960292,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('d167db24-618b-494f-ad08-66e19590c4f1',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9143705560721, 40.753826109439686), 4326)::geography,
        -111.9143705560721,
        40.753826109439686,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('07bbb4c4-71b3-4cf0-9099-b6840f1a3b39',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89976765023084, 40.771074890223424), 4326)::geography,
        -111.89976765023084,
        40.771074890223424,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('2a53de5d-9dea-4905-ac57-372371423efa',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.94581477865084, 40.801147609514096), 4326)::geography,
        -111.94581477865084,
        40.801147609514096,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('8bbf49b2-c7f9-49a1-afc3-064032d012f1',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91632556506195, 40.78898966182583), 4326)::geography,
        -111.91632556506195,
        40.78898966182583,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('37a34d84-e95c-4e7d-82ee-6d0340b337b2',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9195971995211, 40.76148728609713), 4326)::geography,
        -111.9195971995211,
        40.76148728609713,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('281c1e12-2cb1-40c0-b758-d4a21ac0f67d',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.92285340682236, 40.794024819446655), 4326)::geography,
        -111.92285340682236,
        40.794024819446655,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('28c95bd5-e68f-4f3d-871e-787f80c4dc71',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88978107583256, 40.75269693253255), 4326)::geography,
        -111.88978107583256,
        40.75269693253255,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('0afe86c7-3d46-426b-8e7a-d0a2feca49f8',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89775203515366, 40.7665666998244), 4326)::geography,
        -111.89775203515366,
        40.7665666998244,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('3d0e713e-ec1b-4003-aa35-04ca2ae791d8',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.87522893348174, 40.768452128718096), 4326)::geography,
        -111.87522893348174,
        40.768452128718096,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('6b088c73-c84c-4d64-99ba-45ba8f4c1dfb',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.87403149937543, 40.7456886379437), 4326)::geography,
        -111.87403149937543,
        40.7456886379437,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('171e1c04-108c-432e-a643-5bd50c5d807f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9186122807498, 40.74632901557367), 4326)::geography,
        -111.9186122807498,
        40.74632901557367,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('8853d4c1-de91-49e9-a158-9bba280f442f',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91880683659565, 40.72574836945068), 4326)::geography,
        -111.91880683659565,
        40.72574836945068,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('df611e20-b865-466d-b96c-2c354484b327',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.94485434597587, 40.73995283818972), 4326)::geography,
        -111.94485434597587,
        40.73995283818972,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('827d76ed-b3b4-4279-b972-766f884a21b0',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89958270739521, 40.76110953195456), 4326)::geography,
        -111.89958270739521,
        40.76110953195456,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('7c8831fc-b45a-47d6-a10e-4a3dd864a7f7',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.91874880537092, 40.76791564529171), 4326)::geography,
        -111.91874880537092,
        40.76791564529171,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('af81a201-a420-4cd6-8032-0a438e867ae7',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.85945347229513, 40.71322278136103), 4326)::geography,
        -111.85945347229513,
        40.71322278136103,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('c6eb14e0-8300-4554-b185-413fcbfe6eeb',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.9280552331382, 40.74722551145181), 4326)::geography,
        -111.9280552331382,
        40.74722551145181,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('9336c738-e54c-45ee-9144-9971c22ee672',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.86107261858368, 40.76822741032053), 4326)::geography,
        -111.86107261858368,
        40.76822741032053,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('5a708abb-55eb-48e4-9c1e-635b5063b9bc',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88544609431732, 40.739904387374956), 4326)::geography,
        -111.88544609431732,
        40.739904387374956,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('870cb14f-6617-495c-9ef9-4c700ac9735e',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.89775203515366, 40.7665666998244), 4326)::geography,
        -111.89775203515366,
        40.7665666998244,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('996b396c-68ae-40f4-b0fc-af55fa56d89a',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.88635130613504, 40.772212062204396), 4326)::geography,
        -111.88635130613504,
        40.772212062204396,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('af5b8791-abef-49ae-9b55-f2f73abc218c',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.93936027331152, 40.77263551012719), 4326)::geography,
        -111.93936027331152,
        40.77263551012719,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('fd8bed54-9970-489c-ac53-933d3234c4c3',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.93131632224824, 40.766349713334705), 4326)::geography,
        -111.93131632224824,
        40.766349713334705,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('97bf8869-428d-4f94-8c00-28d0b41b5bb7',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.86542128926001, 40.76057002285993), 4326)::geography,
        -111.86542128926001,
        40.76057002285993,
        ARRAY []::UUID[]);
INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('20ea0119-ebe0-477e-a549-42cc564b0854',
        '75e46d20e0d941c1af604d354dd46ca0',
        1,
        ST_SetSRID(ST_Point(-111.8767185130215, 40.71605349634576), 4326)::geography,
        -111.8767185130215,
        40.71605349634576,
        ARRAY []::UUID[]);
