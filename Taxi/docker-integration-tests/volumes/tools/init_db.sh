#!/usr/bin/env bash

set -e

/taxi/tools/run.py \
    --wait mongo.taxi.yandex:27017 \
           redis.taxi.yandex:6379 \
    --run /taxi/bootstrap_db/create_db_users.sh
/taxi/bootstrap_db/bootstrap_db.py --force

# hack for config with dots in keys
mongo --eval \
    'db.config.insert({"_id": "LOOKUP_ORDER_CORE_MAPPING", "v": {"_id": "order_id", "adverse_destination": "", "aliases.due": "", "aliases.generation": "", "aliases.id": "", "autoreorder.decisions.created": "", "candidates.alias_id": "", "candidates.car_number": "", "candidates.db_id": "", "candidates.driver_id": "", "candidates.driver_license_personal_id": "candidates.license_id", "candidates.skipped": "", "extra_data.code_dispatch.code": "", "lookup.eta": "lookup.start_eta", "lookup.generation": "", "lookup.state.next_call_eta": "lookup.next_call_eta", "lookup.state.wave": "lookup.wave", "lookup.version": "", "manual_dispatch": "", "order._type": "", "order.calc.alternative_type": "", "order.calc.distance": "", "order.calc.time": "", "order.city": "", "order.created": "", "order.decoupling": "", "order.discount.by_classes": "", "order.feedback.mqc": "", "order.fixed_price.paid_supply_info": "", "order.fixed_price.paid_supply_price": "", "order.fixed_price.price": "", "order.nz": "order.nearest_zone", "order.pricing_data.is_fallback": "", "order.request.cargo_ref_id": "order.cargo_ref_id", "order.request.check_new_logistic_contract": "", "order.request.class": "", "order.request.comment": "", "order.request.corp.client_id": "", "order.request.destinations.geopoint": "", "order.request.dispatch_type": "", "order.request.due": "", "order.request.excluded_parks": "", "order.request.ignore_excluded_parks": "", "order.request.is_delayed": "", "order.request.lookup_ttl": "", "order.request.offer": "", "order.request.requirements": "", "order.request.source.geopoint": "", "order.request.source.object_type": "", "order.request.source_geoareas": "", "order.request.sp": "order.request.surge_price", "order.request.spr": "order.request.surge_price_required", "order.request.white_label_requirements": "", "order.source": "", "order.surge_upgrade_classes": "", "order.svo_car_number": "", "order.user_agent": "", "order.user_id": "", "order.user_phone_id": "", "order.user_tags": "", "order.user_uid": "", "order.using_new_pricing": "", "order.virtual_tariffs": "", "order_info.statistics.status_updates.q": "", "order_info.statistics.status_updates.s": "", "payment_tech.complements": "", "payment_tech.type": "", "status": ""}})' mongo.taxi.yandex:27017/dbtaxi
