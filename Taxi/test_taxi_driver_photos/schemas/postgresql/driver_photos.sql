\set role testsuite
\ir ../../../postgresql/driver_photos/migrations/V01__initial_schema.sql
\ir ../../../postgresql/driver_photos/migrations/V02__park_driver_id.sql
\ir ../../../postgresql/driver_photos/migrations/V03__photo_priority_and_reason.sql
\ir ../../../postgresql/driver_photos/migrations/V04__unique_driver_id_index.sql
\ir ../../../postgresql/driver_photos/migrations/V05__photo_name_and_status_indexes.sql
\ir ../../../postgresql/driver_photos/migrations/V06__updated_time_field_and_trigger.sql
\ir ../../../postgresql/driver_photos/migrations/V07__updated_time_for_admin.sql
\ir ../../../postgresql/driver_photos/migrations/V08__is_deleted.sql
\ir ../../../postgresql/driver_photos/migrations/V09__NONTRANSACTIONAL_is_deleted_index.sql
