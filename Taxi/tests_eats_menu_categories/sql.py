import psycopg2.extras

from tests_eats_menu_categories import models


def insert_item(database, menu_item: models.MenuItem):
    database.cursor().execute(
        """
        INSERT INTO menu_categories.items (
            id,
            place_id
        ) VALUES (
            %s,
            %s
        )
        """,
        (menu_item.menu_item_id, menu_item.place_id),
    )


def insert_rule(database, rule: models.Rule):
    database.cursor().execute(
        """
        INSERT INTO menu_categories.rules (
            id,
            slug,
            name,
            effect,
            category_ids,
            type,
            enabled,
            payload,
            created_at,
            updated_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            rule.rule_id,
            rule.slug,
            rule.name,
            rule.effect.value,
            rule.category_ids,
            rule.type.value,
            rule.enabled,
            psycopg2.extras.Json(rule.payload),
            rule.created_at,
            rule.updated_at,
        ),
    )


def insert_category(database, category: models.Category):
    database.cursor().execute(
        """
        INSERT INTO menu_categories.categories (
            id,
            slug,
            name,
            status,
            created_at,
            updated_at,
            created_by,
            updated_by
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            category.category_id,
            category.slug,
            category.name,
            category.status.value,
            category.created_at,
            category.updated_at,
            category.created_by,
            category.updated_by,
        ),
    )


def insert_mapping(database, mapping: models.Mapping):
    database.cursor().execute(
        """
        INSERT INTO menu_categories.items_categories (
            item_id,
            category_id,
            score,
            rule_id
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            mapping.menu_item_id,
            mapping.category_id,
            mapping.score,
            mapping.rule_id,
        ),
    )
