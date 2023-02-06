INSERT INTO combo_contractors.contractor (
  chunk_id, dbid_uuid, order_id, updated, position,
  source, destination, left_time, left_distance,
  tariff_class, tariff_zone, calc_alternative_type,
  promised_timestamp, orders
)
VALUES 
(
  0, 'dbid_uuid0', 'order_id0', '2001-9-9 01:46:39', 
  '(37.66, 55.73)', '(37.66, 55.73)', '(37.66, 55.71)', '00:10:00', 1000.0, 
  'comfort', 'moscow', 'outer_combo', '2001-9-9 01:56:39',
  '{"orders": [
      {
          "calc_alternative_type": "combo",
          "chunk_id": 0,
          "corp_client_id": "corp_client_id_ok",
          "dbid_uuid": "dbid_uuid0",
          "destination": [37.66, 55.75],
          "event_index": 0,
          "has_chain_parent": false,
          "has_comment": false,
          "order_id": "order_id0",
          "payment_type": "card",
          "plan_transporting_distance": 4300.0,
          "plan_transporting_time": 43,
          "ready_status": "pending",
          "source": [37.66, 55.75],
          "tariff_class": "econom",
          "tariff_zone": "moscow",
          "taxi_status": "transporting",
          "transporting_started_at": "2001-09-09T01:46:39+0000",
          "updated": "2001-09-09T01:46:39+0000",
          "user_phone_id": "507f1f77bcf86cd799439011",
          "destinations_changed_at": "2001-09-09T01:46:39+0000",
          "driving_started_at": "2001-09-09T01:40:39+0000"}]
    }'
),
(
  0, 'dbid_uuid1', 'order_id1', '2001-9-9 01:46:39', 
  '(37.66, 55.74)', '(37.66, 55.74)', '(37.66, 55.70)', '00:20:00', 2000.0, 
  'comfort', 'moscow', 'outer_combo', '2001-9-9 02:06:39',
  '{"orders": [
      {
          "calc_alternative_type": "combo",
          "chunk_id": 0,
          "corp_client_id": "corp_client_id_ok",
          "dbid_uuid": "dbid_uuid1",
          "destination": [37.66, 55.75],
          "event_index": 0,
          "has_chain_parent": false,
          "has_comment": false,
          "order_id": "order_id1",
          "payment_type": "card",
          "plan_transporting_distance": 4300.0,
          "plan_transporting_time": 43,
          "ready_status": "pending",
          "source": [37.66, 55.75],
          "tariff_class": "econom",
          "tariff_zone": "moscow",
          "taxi_status": "transporting",
          "transporting_started_at": "2001-09-09T01:46:39+0000",
          "updated": "2001-09-09T01:46:39+0000",
          "user_phone_id": "507f1f77bcf86cd799439011",
          "destinations_changed_at": "2001-09-09T01:46:39+0000",
          "driving_started_at": "2001-09-09T01:40:39+0000"}]
    }'
),
(
  1, 'dbid_uuid2', 'order_id2', '2001-9-9 01:46:39', 
  '(37.66, 55.75)', '(37.66, 55.75)', '(37.66, 55.69)', '00:30:00', 3000.0, 
  '', '', 'combo_order', '2001-9-9 02:16:39',
  '{"orders": [
      {
          "calc_alternative_type": "combo",
          "chunk_id": 0,
          "corp_client_id": "corp_client_id_ok",
          "dbid_uuid": "dbid_uuid2",
          "destination": [37.66, 55.75],
          "event_index": 0,
          "has_chain_parent": false,
          "has_comment": false,
          "order_id": "order_id2",
          "payment_type": "card",
          "plan_transporting_distance": 4300.0,
          "plan_transporting_time": 43,
          "ready_status": "pending",
          "source": [37.66, 55.75],
          "tariff_class": "econom",
          "tariff_zone": "moscow",
          "taxi_status": "transporting",
          "transporting_started_at": "2001-09-09T01:46:39+0000",
          "updated": "2001-09-09T01:46:39+0000",
          "user_phone_id": "507f1f77bcf86cd799439011",
          "destinations_changed_at": "2001-09-09T01:46:39+0000",
          "driving_started_at": "2001-09-09T01:40:39+0000"}]
    }'

),
(
  2, 'dbid_uuid3', 'order_id3', '2001-9-9 01:46:39', 
  '(37.66, 55.75)', '(37.66, 55.75)', '(37.66, 55.69)', '00:20:00', 3000.0, 
  '', '', 'combo_check_1', '2001-9-9 02:06:39',
  '{"orders": [
      {
          "calc_alternative_type": "combo",
          "chunk_id": 0,
          "corp_client_id": "corp_client_id_ok",
          "dbid_uuid": "dbid_uuid3",
          "destination": [37.66, 55.75],
          "event_index": 0,
          "has_chain_parent": false,
          "has_comment": false,
          "order_id": "order_id3",
          "payment_type": "card",
          "plan_transporting_distance": 4300.0,
          "plan_transporting_time": 43,
          "ready_status": "pending",
          "source": [37.66, 55.75],
          "tariff_class": "econom",
          "tariff_zone": "moscow",
          "taxi_status": "transporting",
          "transporting_started_at": "2001-09-09T01:46:39+0000",
          "updated": "2001-09-09T01:46:39+0000",
          "user_phone_id": "507f1f77bcf86cd799439011",
          "destinations_changed_at": "2001-09-09T01:46:39+0000",
          "driving_started_at": "2001-09-09T01:40:39+0000"}]
    }'
),
(
  3, 'dbid_uuid4', 'order_id4', '2001-9-9 01:46:39', 
  '(37.66, 55.75)', '(37.66, 55.75)', '(37.66, 55.69)', '00:40:00', 3000.0, 
  '', '', 'combo_check_1', '2001-9-9 02:26:39',
  '{"orders": [
      {
          "calc_alternative_type": "combo",
          "chunk_id": 0,
          "corp_client_id": "corp_client_id_ok",
          "dbid_uuid": "dbid_uuid4",
          "destination": [37.66, 55.75],
          "event_index": 0,
          "has_chain_parent": false,
          "has_comment": false,
          "order_id": "order_id4",
          "payment_type": "card",
          "plan_transporting_distance": 4300.0,
          "plan_transporting_time": 43,
          "ready_status": "pending",
          "source": [37.66, 55.75],
          "tariff_class": "econom",
          "tariff_zone": "moscow",
          "taxi_status": "transporting",
          "transporting_started_at": "2001-09-09T01:46:39+0000",
          "updated": "2001-09-09T01:46:39+0000",
          "user_phone_id": "507f1f77bcf86cd799439011",
          "destinations_changed_at": "2001-09-09T01:46:39+0000",
          "driving_started_at": "2001-09-09T01:40:39+0000"}]
    }'
);
