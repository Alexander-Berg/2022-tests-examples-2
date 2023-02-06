ALTER TABLE cargo_dispatch.admin_segment_reorders DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segment_involved_routers DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segments DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segments_change_log DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybill_points DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybill_segments DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybills DISABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybills_change_log DISABLE TRIGGER ALL;

INSERT INTO cargo_dispatch.admin_segment_reorders
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.admin_segment_reorders,
'{
  "cancel_request_token": "cargo-dispatch/12345",
  "created_at": "2021-01-01T00:00:04+00:00",
  "forced_action": "reorder_by_support_logics",
  "reason": "performer_mistake.other",
  "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459",
  "source": "segment/autoreorder",
  "ticket": "b304df2edc604bfa8d0672091c7db593",
  "updated_ts": "2021-01-01T01:00:04+00:00",
  "waybill_building_version": 1
}'
);

INSERT INTO cargo_dispatch.segment_involved_routers
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.segment_involved_routers,
'{
  "autoreorder_flow": "oldway",
  "is_deleted": false,
  "priority": 1,
  "router_id": "fallback_router",
  "router_source": "cargo-dispatch-choose-routers:segment_routers:some_clause",
  "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459"
}'
);

INSERT INTO cargo_dispatch.segments
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.segments,
'{
 "allow_alive_batch_v1": false,
 "allow_alive_batch_v2": true,
 "chosen_waybill": "default_router/bba87676-8d5e-45ec-8b21-b890cd3e5f93",
 "claim_id": "394709a02bcf429795cc13b295c79cef",
 "claims_notified_on_orders_changes_version": 16,
 "claims_segment_created_ts": "2021-01-01T02:00:04+00:00",
 "claims_segment_revision": 2,
 "created_ts": "2021-01-01T00:00:04+00:00",
 "dynamic_context": {
   "delivery_flags": {
     "is_forbidden_to_be_in_batch": true
   }
 },
 "first_lookup_started_at": "2021-01-01T06:00:04+00:00",
 "is_cancelled_by_user": false,
 "orders_changes_version": 15,
 "points_user_version": 5,
 "resolution": "failed",
 "revision": 10,
 "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459",
 "status": "resolved",
 "updated_ts": "2021-01-01T01:00:04+00:00",
 "waybill_building_deadline": "2021-01-01T05:00:04+00:00",
 "waybill_building_version": 3
}'
);

INSERT INTO cargo_dispatch.segments_change_log
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.segments_change_log,
'{
  "event_time": "2021-01-01T15:00:04+00:00",
  "id": 5,
  "new_status": "routers_chosen",
  "old_status": "new",
  "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459",
  "updated_ts": "2021-01-01T05:00:04+00:00"
}'
);

INSERT INTO cargo_dispatch.waybill_points
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.waybill_points,
'{
  "estimated_distance_of_arrival": 383,
  "estimated_time_of_arrival": "2021-01-01T05:00:04+00:00",
  "eta_calculation_awaited": true,
  "id": 1,
  "is_approximate": true,
  "performer_comment": "waybill point comment",
  "point_id": "cc24d37d-aa9c-4222-8380-f9dae0500b9a",
  "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459",
  "updated_ts": "2021-01-01T05:00:04+00:00",
  "visit_order": 6,
  "waybill_external_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7"
}'
);

INSERT INTO cargo_dispatch.waybill_segments
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.waybill_segments,
'{
  "segment_id": "abe645fc-14d2-4cda-ba58-af5e55ff1459",
  "updated_ts": "2021-01-01T05:00:04+00:00",
  "waybill_building_version": 1,
  "waybill_external_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7"
}'
);

INSERT INTO cargo_dispatch.waybills
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.waybills,
'{
  "autoreorder_flow": "newway",
  "cancel_state": "free",
  "chain_parent_cargo_order_id": "c0e2a013-2da3-483b-8501-89a73eda7bcd",
  "claims_changes_version": 7,
  "created_ts": "2021-01-01T05:00:04+00:00",
  "external_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7",
  "extra_time_min": 1200,
  "handle_processing_claims_changes_version": 5,
  "initial_waybill_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7",
  "is_actual_waybill": true,
  "last_taximeter_state_version_increment_idempotency_token": "1234567890abcdef",
  "need_commit": false,
  "order_expired_ts": "2021-01-01T05:00:04+00:00",
  "order_fail_reason": "performer_not_found",
  "order_id": "2c6176b4-693b-40ff-92d2-084fa707b08a",
  "order_last_performer_found_ts": "2021-01-01T05:00:04+00:00",
  "order_revision": 2,
  "orders_notify_claims_changes_version": 7,
  "paper_flow": false,
  "previous_waybill_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7",
  "priority": 1,
  "proposal_kind": "fail_segments",
  "resolution": "complete",
  "resolved_at": "2021-01-01T05:00:04+00:00",
  "revision": 20,
  "router_id": "logistic-dispatch",
  "special_requirements": {
    "virtual_tariffs": [
      {
        "class": "courier"
      }
    ]
  },
  "status": "resolved",
  "stq_create_orders_was_set": true,
  "taxi_lookup_extra": {
      "intent": "grocery-manual",
      "performer_id": "performer_hash"
  },
  "taxi_order_id": "db55c5a7c465467aa2fdf6ed8f898241",
  "taxi_order_requirements": {
    "door_to_door": true,
    "taxi_classes": [
      "courier",
      "eda",
      "express"
    ]
  },
  "taximeter_state_version": 6,
  "updated_ts": "2021-01-01T05:00:04+00:00",
  "waybill_building_deadline": "2021-01-01T05:00:04+00:00",
  "waybills_created_ts": "2021-01-01T05:00:04+00:00",
  "waybills_updated_ts": "2021-01-01T05:00:04+00:00"
}'
);

INSERT INTO cargo_dispatch.waybills_change_log
SELECT *
FROM json_populate_record (NULL::cargo_dispatch.waybills_change_log,
'{
  "event_time": "2021-01-01T05:00:04+00:00",
  "external_ref": "logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7",
  "id": 5,
  "new_status": "resolved",
  "old_status": "processing",
  "updated_ts": "2021-01-01T05:00:04+00:00"
}'
);

ALTER TABLE cargo_dispatch.admin_segment_reorders ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segment_involved_routers ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segments ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.segments_change_log ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybill_points ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybill_segments ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybills ENABLE TRIGGER ALL;
ALTER TABLE cargo_dispatch.waybills_change_log ENABLE TRIGGER ALL;
