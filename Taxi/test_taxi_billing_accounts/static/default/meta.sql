DO $$
DECLARE
    BA_VSHARD_PFX varchar := 'ba_testsuite_';
    PSHARD_COUNT integer := 2;
    VSHARD_COUNT integer := 8;
BEGIN
    INSERT INTO ba_testsuite_meta.config(key, value)
    VALUES ('pshard_count',  PSHARD_COUNT),
           ('vshard_count',  VSHARD_COUNT),
           ('vshard_prefix', BA_VSHARD_PFX)
    ;

    INSERT INTO ba_testsuite_meta.vshard(id, pshard_id)
    SELECT v.id, v.id/(VSHARD_COUNT/PSHARD_COUNT)
      FROM (SELECT generate_series(0, VSHARD_COUNT - 1) id) v
    ;
END;
$$ LANGUAGE plpgsql;
