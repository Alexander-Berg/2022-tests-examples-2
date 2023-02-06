--workaround for testsuite
DO
  $do$
    BEGIN
      IF NOT EXISTS (
          SELECT
          FROM   pg_catalog.pg_roles
          WHERE  rolname = 'taxiro') THEN
        CREATE ROLE taxiro;
      END IF;
    END
  $do$;
