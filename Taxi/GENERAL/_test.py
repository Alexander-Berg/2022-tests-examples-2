import business_models as bm
from business_models import hahn
hahn.change_token("robot_taxi_analyst_token")
from business_models.hahn import HahnDataLoader
hahn.save_links = True
from business_models import greenplum


hahn("select 'Other_token_works'")
