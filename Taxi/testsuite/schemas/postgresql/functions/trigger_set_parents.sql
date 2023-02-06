CREATE OR REPLACE FUNCTION trigger_set_parents()
    RETURNS TRIGGER AS $$
DECLARE
    parent_parents integer[];
BEGIN
    IF TG_OP = 'INSERT' THEN
        parent_parents := (
            SELECT
                parents
            from
                access_control.groups
            WHERE
                id=NEW.parent_id
        );
        IF parent_parents IS NOT NULL THEN
            NEW.parents = NEW.parent_id || parent_parents;
        ELSE
            IF NEW.parent_id IS NOT NULL THEN
                NEW.parents = array[NEW.parent_id];
            ELSE
                NEW.parents = array[]::integer[];
            END IF;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
