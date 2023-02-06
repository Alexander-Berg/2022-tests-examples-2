# import os
# import sys
#
# import ammo
# import tpl_db as tpl_db
#
# user_home = os.getenv("HOME")
# sys.path.append(user_home + '/arc/arcadia')
#
#
# default_profile = {
#     ammo.TplTrackingRandomRequestGenerator.get_tracking: 10,
#     ammo.TplTrackingRandomRequestGenerator.get_tracking_courier_location: 1,
# }
#
# print("Connecting to db...")
# db = tpl_db.TplDB(
#     host='sas-4tmekbxz3h755f5c.db.yandex.net',
#     username='market_tpl_production',
#     password='ProdStress_P@ss',
#     dbname='market_tpl_production'
# )
# tracking_ids = ['123']
# print('Obtained tracking ids')
# print(tracking_ids)
#
# print("Generating ammo...")
# ammo.generate_ammo(
#     bullet_count=10,
#     profile=default_profile,
#     host='localhost:228',
#     tracking_ids=tracking_ids
# )
# print("Done! Saving...")
#
# print("Saved!")
