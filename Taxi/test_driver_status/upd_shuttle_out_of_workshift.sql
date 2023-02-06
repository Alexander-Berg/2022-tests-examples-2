UPDATE state.shuttle_trip_progress
SET block_reason = 'out_of_workshift'
WHERE shuttle_id = 1
