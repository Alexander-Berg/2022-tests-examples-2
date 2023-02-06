\set role testsuite
\ir ../../../postgresql/pricing-modifications-validator/migrations/V01__initial.sql
\ir ../../../postgresql/pricing-modifications-validator/migrations/V02__denormalized_data.sql
\ir ../../../postgresql/pricing-modifications-validator/migrations/V03__index_on_denormalized_data.sql
\ir ../../../postgresql/pricing-modifications-validator/migrations/V04__add_script_tasks_message.sql
\ir ../../../postgresql/pricing-modifications-validator/migrations/V05__add_new_storage_tables.sql
