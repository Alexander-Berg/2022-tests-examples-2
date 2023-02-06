DO $$
BEGIN
    EXECUTE format(
          'alter table eats_picker_item_categories.item_categories drop constraint  %s', (
          select constraint_name
            from information_schema.table_constraints
            where table_schema = 'eats_picker_item_categories'
                  and table_name = 'item_categories'
                  and constraint_type = 'PRIMARY KEY'
                  )
      );
            END
$$
LANGUAGE plpgsql;

BEGIN;
ALTER TABLE eats_picker_item_categories.item_categories ADD PRIMARY KEY (item_id, category_id, hierarchy_number);

COMMIT;
