from business_models import greenplum, hahn


df = greenplum("select * from core_cdm_geo.v_dim_fi_geo_hierarchy")
print(df)