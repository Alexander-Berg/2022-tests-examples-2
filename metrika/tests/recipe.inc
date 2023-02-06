SET(CLICKHOUSE_RECIPE_OPTS
    --execute metrika/admin/python/scripts/clickhouse_parts_cleaner/tests/tables.sql
)

INCLUDE(${ARCADIA_ROOT}/library/recipes/clickhouse/recipe.inc)