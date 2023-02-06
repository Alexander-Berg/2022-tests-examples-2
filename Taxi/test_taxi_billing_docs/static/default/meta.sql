DO $$
DECLARE
    BD_VSHARD_PFX varchar := 'bd_testsuite_';
    PSHARD_COUNT integer := 2;
    VSHARD_COUNT integer := 8;
BEGIN
    INSERT INTO bd_testsuite_meta.config(key, value)
    VALUES ('pshard_count',  PSHARD_COUNT),
           ('vshard_count',  VSHARD_COUNT),
           ('vshard_prefix', BD_VSHARD_PFX)
    ;

    INSERT INTO bd_testsuite_meta.vshard(id, pshard_id, ro_pshard_id)
    SELECT v.id, v.id/(VSHARD_COUNT/PSHARD_COUNT), v.id/(VSHARD_COUNT/PSHARD_COUNT)
      FROM (SELECT generate_series(0, VSHARD_COUNT - 1) id) v
    ;
END;
$$ LANGUAGE plpgsql;
