DROP SCHEMA IF EXISTS access_control CASCADE;
CREATE SCHEMA access_control;

\ir ./functions/trigger_set_updated_at_timestamp.sql
\ir ./functions/trigger_set_parents.sql

\ir ./tables/system.sql
\ir ./tables/users.sql
\ir ./tables/groups.sql
\ir ./tables/roles.sql
\ir ./tables/permissions.sql
\ir ./tables/m2m_groups_users.sql
\ir ./tables/m2m_groups_roles.sql
\ir ./tables/m2m_permissions_roles.sql
\ir ./tables/restrictions.sql
\ir ./tables/permission_calculation_rules.sql
\ir ./tables/calculated_permissions.sql
