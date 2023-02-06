--
-- create local environment: pshard 2 of 2
----------------------------------------------------------------

SET client_min_messages TO WARNING;
\ir config.psql
\ir ../../../storage/schema/00.vars.psql
\ir ../../../storage/schema/meta.ddl.psql
\ir ../../../storage/schema/meta.dml.psql

\set ba_vshard :ba_vshard_pfx 04
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 05
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 06
\ir ../../../storage/schema/create.vshard.psql
\set ba_vshard :ba_vshard_pfx 07
\ir ../../../storage/schema/create.vshard.psql
