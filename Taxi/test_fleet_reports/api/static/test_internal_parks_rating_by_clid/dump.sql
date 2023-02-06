CREATE TABLE yt.report_parks_rating_by_clid_2021_04 (LIKE yt.report_parks_rating_by_clid);
CREATE TABLE yt.report_parks_rating_by_clid_2021_05 (LIKE yt.report_parks_rating_by_clid);
CREATE TABLE yt.report_parks_rating_by_clid_2021_06 (LIKE yt.report_parks_rating_by_clid);



ALTER TABLE yt.report_parks_rating_by_clid_2021_04
ADD CONSTRAINT report_parks_rating_by_clid_2021_04_date_at_check
CHECK (date_at_min >= '2021-04-01'::date AND date_at_min <= '2021-04-30'::date);

ALTER TABLE yt.report_parks_rating_by_clid_2021_05
ADD CONSTRAINT report_parks_rating_by_clid_2021_05_date_at_check
CHECK (date_at_min >= '2021-05-01'::date AND date_at_min <= '2021-05-31'::date);

ALTER TABLE yt.report_parks_rating_by_clid_2021_06
ADD CONSTRAINT report_parks_rating_by_clid_2021_06_date_at_check
CHECK (date_at_min >= '2021-06-01'::date AND date_at_min <= '2021-06-30'::date);



ALTER TABLE yt.report_parks_rating_by_clid_2021_04 INHERIT yt.report_parks_rating_by_clid;
ALTER TABLE yt.report_parks_rating_by_clid_2021_05 INHERIT yt.report_parks_rating_by_clid;
ALTER TABLE yt.report_parks_rating_by_clid_2021_06 INHERIT yt.report_parks_rating_by_clid;



INSERT INTO 
        yt.report_parks_rating_by_clid_2021_04 (id, clid, date_at_min, date_at_max, tier)
VALUES 
        (2, 'test_clid_1', '2021-04-20', '2021-04-30', 'bronze')
;

INSERT INTO 
        yt.report_parks_rating_by_clid_2021_05 (id, clid, date_at_min, date_at_max, tier)
VALUES 
        (1, 'test_clid_1', '2021-05-20', '2021-05-31', 'weak'), 
        (3, 'test_clid_2', '2021-05-10', '2021-05-15', 'gold'),
        (4, 'test_clid_3', '2021-05-20', '2021-05-31', 'gold'),
        (6, 'test_clid_3', '2021-05-18', '2021-05-19', 'weak')
;

INSERT INTO 
        yt.report_parks_rating_by_clid_2021_06 (id, clid, date_at_min, date_at_max, tier)
VALUES 
        (5, 'test_clid_3', '2021-06-01', '2021-06-22', 'small'),
        (7, 'test_clid_3', '2021-06-23', '2021-06-25', 'gold'),
        (8, 'test_clid_3', '2021-06-26', '2021-06-29', 'bronze'),
        (9, 'test_clid_4', '2021-06-01', '2021-06-03', 'small')
;
