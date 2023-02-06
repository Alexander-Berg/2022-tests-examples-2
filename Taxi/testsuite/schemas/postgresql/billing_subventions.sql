DROP SCHEMA IF EXISTS subventions CASCADE;

\set role_svc testsuite
\set role_ro testsuite

\ir ../../../../../../schemas/schemas/postgresql/billing_subventions_x/init.sql
