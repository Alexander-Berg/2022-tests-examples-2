--
-- create local environment: pshard 1 of 2
----------------------------------------------------------------

SET client_min_messages TO WARNING;
\ir config.psql
\ir ../../../storage/schema/00.vars.psql
\ir ../../../storage/schema/meta.ddl.psql
\ir ../../../storage/schema/meta.dml.psql

\set ba_vshard :ba_vshard_pfx 00
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 01
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 02
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 03
\ir ../../../storage/schema/create.vshard.psql
