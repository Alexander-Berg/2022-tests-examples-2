# import sys
# import os
# import codecs

# user_home = os.getenv("HOME")
# sys.path.append(user_home + '/arc/arcadia')

# import ammo

# datacenter_count = 3
# orders_per_status_per_pp = 200
# bullets = 17000

# default_profile = {
#     # ds api
#     ammo.create_order: 0.83,
#     ammo.update_order: 1.60,
#     ammo.get_order_status: 15,
#     ammo.get_order_history: 65,
#     # partner
#     ammo.get_order_list: 0.28,
#     ammo.deliver_order: 0.83,
# }

# target_rps = 0
# for (key, value) in default_profile.items():
#     target_rps += value

# rps_per_dc = round(target_rps / datacenter_count)
# count = 10 * 60 * rps_per_dc

# print('Target RPS per DC: ' + str(round(rps_per_dc)))
# print('Target count for 10m: >= ' + str(count))

# print("Generating ammo...")
# ammo_text = ammo.generate_ammo(bullets, orders_per_status_per_pp, default_profile)
# print("Done! Saving...")

# ammo_file = user_home + '/dev/pvz-int_ammo.txt'
# with codecs.open(ammo_file, 'w', encoding='utf-8') as f:
#     f.write(ammo_text)
# print("Saved!")

