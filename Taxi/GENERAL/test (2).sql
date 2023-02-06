DROP TABLE snb_eda.alexlytics_marketing_dash_tmp;
CREATE TABLE snb_eda.alexlytics_marketing_dash_tmp as (
    select *
    from snb_eda.yametrika_perfomance_ods
    limit 10
)