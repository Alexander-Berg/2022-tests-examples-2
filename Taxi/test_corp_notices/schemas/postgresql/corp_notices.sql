\set role testsuite
\ir ../../../postgresql/corp_notices/migrations/V01__create_db.sql
\ir ../../../postgresql/corp_notices/migrations/V02__add_token.sql
\ir ../../../postgresql/corp_notices/migrations/V03__NONTRANSACTIONAL_add_dequeue_status.sql
