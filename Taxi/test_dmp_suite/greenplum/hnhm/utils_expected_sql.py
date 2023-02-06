# coding: utf-8

EXCEPTED_SQL_ACTUAL_ALL = """
SELECT "a1"."attr_new" as "attr_new"
  , "a2"."dt" as "dt"
  , "a3"."entity_id" as "entity_id"
  , "a4"."value" as "value"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr_new__h2") "a1"
            ON "a1".id = h.id AND
               "a1".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__dt") "a2"
            ON "a2".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity_id__key") "a3"
            ON "a3".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__value") "a4"
            ON "a4".id = h.id
"""

EXCEPTED_SQL_ACTUAL_PROJECT = """
SELECT "a1"."attr_new" as "abc"
  , "a2"."dt" as "dt"
  , "a3"."value" as "value"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr_new__h2") "a1"
            ON "a1".id = h.id AND
               "a1".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__dt") "a2"
            ON "a2".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__value") "a3"
            ON "a3".id = h.id
"""


EXCEPTED_SQL_HISTORY_ALL = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr2" as "attr2"
  , "a3"."attr3" as "attr3"
  , "a4"."attr4" as "attr4"
  , "a5"."entity2_id" as "entity2_id"
  , "a6"."nr" as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a3".utc_valid_from_dttm AND "a3".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a4"
            ON "a4".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a4".utc_valid_from_dttm AND "a4".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity2_id__key") "a5"
            ON "a5".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a6"
            ON "a6".id = h.id
"""

EXCEPTED_SQL_HISTORY_PROJECT = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr2" as "attr2"
  , "a3"."attr3" as "attr3"
  , "a4"."nr" as "z"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE _source_id != -1) t) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a3".utc_valid_from_dttm AND "a3".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a4"
            ON "a4".id = h.id
"""


EXPECTED_SQL_LINK1_ACTUAL = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "e2"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK1_ACTUAL_PROJECT = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "zzz"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK1_ACTUAL_PROJECT2 = """
SELECT "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK1_ACTUAL_DEP = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "e2"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""
EXPECTED_SQL_LINK1_ACTUAL_PROJECT_DEP = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "zzz"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""
EXPECTED_SQL_LINK1_ACTUAL_PROJECT2_DEP = """
SELECT "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""
EXPECTED_SQL_LINK2_ACTUAL = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK2_ACTUAL_PROJECT = """
SELECT "{ent2}_e2_2__id" as "ddd"
  , "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK2_ACTUAL_PROJECT2 = """
SELECT "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""
EXPECTED_SQL_LINK2_HISTORY = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""
EXPECTED_SQL_LINK2_HISTORY_PROJECT = """
SELECT "{ent2}_e2_2__id" as "ddd"
  , "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""
EXPECTED_SQL_LINK2_HISTORY_PROJECT2 = """
SELECT "{ent1}_e1__id" as "e1"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_ACTUAL_ALL_WITH_GROUP = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr2"      as "attr2"
  , "a3"."attr3"      as "attr3"
  , "a4"."attr4"      as "attr4"
  , "a5"."attr5"      as "attr5"
  , "a5"."attr6"      as "attr6"
  , "a6"."attr7"      as "attr7"
  , "a6"."attr8"      as "attr8"
  , "a7"."entity3_id" as "entity3_id"
  , "a8"."nr"         as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h
  
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1" 
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               "a3".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a4"
            ON "a4".id = h.id AND
               "a4".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a5"
            ON "a5".id = h.id AND
               "a5".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a6" 
            ON "a6".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity3_id__key") "a7" 
            ON "a7".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a8" 
            ON "a8".id = h.id
"""

EXPECTED_SQL_ACTUAL_PROJECT_WITH_GROUP = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr5" as "attr5"
  , "a3"."attr7" as "attr7"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a3"
            ON "a3".id = h.id
"""

EXPECTED_SQL_ACTUAL_PROJECT_WITH_GROUP2 = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr6" as "attr6"
  , "a3"."attr8" as "attr8"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a3"
            ON "a3".id = h.id
"""

EXPECTED_SQL_HISTORY_ALL_WITH_GROUP = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr2"      as "attr2"
  , "a3"."attr3"      as "attr3"
  , "a4"."attr4"      as "attr4"
  , "a5"."attr5"      as "attr5"
  , "a5"."attr6"      as "attr6"
  , "a6"."attr7"      as "attr7"
  , "a6"."attr8"      as "attr8"
  , "a7"."entity3_id" as "entity3_id"
  , "a8"."nr"         as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2" WHERE _source_id != -1) t) t) t) h
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a3".utc_valid_from_dttm AND "a3".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a4"
            ON "a4".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a4".utc_valid_from_dttm AND "a4".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a5"
            ON "a5".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a5".utc_valid_from_dttm AND "a5".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a6"
            ON "a6".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity3_id__key") "a7"
            ON "a7".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a8"
            ON "a8".id = h.id
"""


EXPECTED_SQL_HISTORY_PROJECT_WITH_GROUP = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr5"    as "attr5"
  , "a3"."attr7"    as "attr7"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2" WHERE _source_id != -1) t) t) t) h
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a3"
            ON "a3".id = h.id
"""


EXPECTED_SQL_HISTORY_PROJECT_WITH_GROUP2 = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr6"    as "attr6"
  , "a3"."attr8"    as "attr8"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2" WHERE _source_id != -1) t) t) t) h
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g1__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a3"
            ON "a3".id = h.id
"""


EXPECTED_SQL_HISTORY_PROJECT_WITHOUT_HIST = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr8"    as "attr8"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h) t) h
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."g__{ent}__g2") "a2"
            ON "a2".id = h.id
"""

EXCEPTED_SQL_HISTORY_ALL_PARTITION = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr2" as "attr2"
  , "a3"."attr3" as "attr3"
  , "a4"."attr4" as "attr4"
  , "a5"."entity4_id" as "entity4_id"
  , "a6"."nr" as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE _source_id != -1) t) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a3".utc_valid_from_dttm AND "a3".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a4"
            ON "a4".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a4".utc_valid_from_dttm AND "a4".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity4_id__key") "a5"
            ON "a5".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a6"
            ON "a6".id = h.id
"""

EXCEPTED_SQL_HISTORY_PROJECT_PARTITION = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr4" as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
"""

EXCEPTED_SQL_HISTORY_PROJECT_PARTITION_2 = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr4" as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") h
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
"""

EXCEPTED_SQL_ACTUAL_ALL_PARTITION = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr2"      as "attr2"
  , "a3"."attr3"      as "attr3"
  , "a4"."attr4"      as "attr4"
  , "a5"."entity4_id" as "entity4_id"
  , "a6"."nr"         as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2") "a3"
            ON "a3".id = h.id AND
               "a3".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a4"
            ON "a4".id = h.id AND
               "a4".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity4_id__key") "a5"
            ON "a5".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr") "a6"
            ON "a6".id = h.id
"""

EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr4"      as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
"""

EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_2 = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr4"      as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}") t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1") "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2") "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
"""

EXCEPTED_SQL_HISTORY_ALL_PARTITION_FILTER = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr2" as "attr2"
  , "a3"."attr3" as "attr3"
  , "a4"."attr4" as "attr4"
  , "a5"."entity4_id" as "entity4_id"
  , "a6"."nr" as "nr"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) h
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE _source_id != -1) t WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE _source_id != -1) t WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr2__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr3__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a3"
            ON "a3".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a3".utc_valid_from_dttm AND "a3".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a4"
            ON "a4".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a4".utc_valid_from_dttm AND "a4".utc_valid_to_dttm
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__entity4_id__key" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a5"
            ON "a5".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__nr" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a6"
            ON "a6".id = h.id
"""

EXCEPTED_SQL_HISTORY_PROJECT_PARTITION_2_FILTER = """
SELECT "a1"."attr1" as "attr1"
  , "a2"."attr4" as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
  , "h"."utc_valid_to_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) h
        UNION
        SELECT t.id, t.utc_valid_from_dttm, "utc_start_dttm"
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE _source_id != -1) t WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a2"
            ON "a2".id = h.id AND
               h.utc_valid_from_dttm BETWEEN "a2".utc_valid_from_dttm AND "a2".utc_valid_to_dttm
"""

EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_FILTER = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr4"      as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
"""

EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_2_FILTER = """
SELECT "a1"."attr1"   as "attr1"
  , "a2"."attr4"      as "attr4"
  , "h"."id"
  , "h"."utc_valid_from_dttm"
  , "h"."utc_start_dttm"
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm
    , "utc_start_dttm"
  FROM (SELECT * FROM "taxi_dds_demand"."h__{ent}" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) h

  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr1" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a1"
            ON "a1".id = h.id
  LEFT JOIN (SELECT * FROM "taxi_dds_demand"."a__{ent}__attr4__h2" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "a2"
            ON "a2".id = h.id AND
               "a2".utc_valid_to_dttm = TIMESTAMP'9999-12-31 23:59:59'
"""

EXPECTED_SQL_LINK_PARTITIONED = """
SELECT "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "{ent4}_e4__id" as "e4"
  , "zz" as "zz"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""

EXPECTED_SQL_LINK_PARTITIONED_PROJECT = """
SELECT "{ent2}_e2__id" as "e2"
  , "zz" as "zz1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""

EXPECTED_SQL_LINK_PARTITIONED_PROJECT_FILTER = """
SELECT "{ent2}_e2__id" as "e2"
  , "zz" as "zz1"
  , "utc_valid_from_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t
WHERE NOT COALESCE(_deleted_flg, FALSE)
AND "utc_valid_to_dttm" = '9999-12-31 23:59:59'
"""

EXPECTED_SQL_LINK_PARTITIONED_HIST = """
SELECT "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "{ent4}_e4__id" as "e4"
  , "zz" as "zz"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK_PARTITIONED_HIST_PROJECT = """
SELECT "{ent2}_e2__id" as "e2"
  , "zz" as "zz1"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}") t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK_PARTITIONED_HIST_PROJECT_FILTER = """
SELECT "{ent2}_e2__id" as "e2"
  , "zz" as "zz1"
  , "utc_valid_from_dttm"
  , "utc_valid_to_dttm"
FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t
WHERE NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2", h.utc_valid_from_dttm, h.utc_valid_to_dttm
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm

    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent1}") h
        UNION
        SELECT t."{ent1}_e1__id", t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE _source_id != -1 AND NOT COALESCE(_deleted_flg, FALSE)) t) t) t) h

  INNER JOIN (SELECT * FROM "taxi_dds_demand"."{link}") "lnk"
            ON "lnk"."{ent1}_e1__id" = h.id AND
               h.utc_valid_from_dttm BETWEEN "lnk".utc_valid_from_dttm AND "lnk".utc_valid_to_dttm AND
               NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PROJECT = """
SELECT "{ent1}_e1__id" as "e1"
  , "{ent2}_e2__id" as "zz1", h.utc_valid_from_dttm, h.utc_valid_to_dttm
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm

    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent1}") h
        UNION
        SELECT t."{ent1}_e1__id", t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE _source_id != -1 AND NOT COALESCE(_deleted_flg, FALSE)) t) t) t) h

  INNER JOIN (SELECT * FROM "taxi_dds_demand"."{link}") "lnk"
            ON "lnk"."{ent1}_e1__id" = h.id AND
               h.utc_valid_from_dttm BETWEEN "lnk".utc_valid_from_dttm AND "lnk".utc_valid_to_dttm AND
               NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PARTITION = """
SELECT "{ent2}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "{ent4}_e4__id" as "e4"
  , "zz" as "zz", h.utc_valid_from_dttm, h.utc_valid_to_dttm
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm

    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent4}" WHERE "utc_start_dttm" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) h
        UNION
        SELECT t."{ent4}_e4__id", t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE _source_id != -1 AND NOT COALESCE(_deleted_flg, FALSE)) t WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) t) h

  INNER JOIN (SELECT * FROM "taxi_dds_demand"."{link}" WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "lnk"
            ON "lnk"."{ent4}_e4__id" = h.id AND
               h.utc_valid_from_dttm BETWEEN "lnk".utc_valid_from_dttm AND "lnk".utc_valid_to_dttm AND
               NOT COALESCE(_deleted_flg, FALSE)
"""

EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PARTITION_KEY_OTHER_PARTITION = """
SELECT "{ent4}_e2__id" as "e2"
  , "{ent2}_e2_2__id" as "e2_2"
  , "{ent4}_e4__id" as "e4"
  , "zz" as "zz", h.utc_valid_from_dttm, h.utc_valid_to_dttm
FROM (
  SELECT t.id
    , t.utc_valid_from_dttm

    , lead(t.utc_valid_from_dttm - INTERVAL '1s', 1, TIMESTAMP'9999-12-31 23:59:59')
      OVER (PARTITION BY t.id ORDER BY t.utc_valid_from_dttm) utc_valid_to_dttm
  FROM (
        SELECT h.id, h.utc_valid_from_dttm
        FROM (SELECT * FROM "taxi_dds_demand"."h__{ent4}") h
        UNION
        SELECT t."{ent4}_e4__id", t.utc_valid_from_dttm
        FROM (SELECT * FROM (SELECT * FROM "taxi_dds_demand"."{link}" WHERE _source_id != -1 AND NOT COALESCE(_deleted_flg, FALSE)) t WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) t) t) h

  INNER JOIN (SELECT * FROM "taxi_dds_demand"."{link}" WHERE "zz" BETWEEN '2020-01-15T00:00:00'::timestamp AND '2020-01-17T23:59:59.999999'::timestamp) "lnk"
            ON "lnk"."{ent4}_e4__id" = h.id AND
               h.utc_valid_from_dttm BETWEEN "lnk".utc_valid_from_dttm AND "lnk".utc_valid_to_dttm AND
               NOT COALESCE(_deleted_flg, FALSE)
"""
