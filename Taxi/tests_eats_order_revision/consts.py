REVISION_SELECT_SQL = """
SELECT
    id,
    order_id,
    origin_revision_id,
    cost_for_customer,
    document,
    is_applied,
    created_at
FROM eats_order_revision.revisions
WHERE order_id = %s AND origin_revision_id = %s
;
"""
REVISION_INSERT_SQL = """
INSERT INTO eats_order_revision.revisions (order_id,
                                           origin_revision_id,
                                           cost_for_customer,
                                           document,
                                           is_applied,
                                           created_at,
                                           version,
                                           service,
                                           initiator)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (order_id, origin_revision_id) DO NOTHING;
;
"""
REVISION_COUNT_SQL = """
SELECT
    COUNT(*)
FROM eats_order_revision.revisions;
;
"""
TAGS_INSERT_SQL = """
INSERT INTO eats_order_revision.revision_tags (revision_id,
                                               tag, created_at)
VALUES (%s, %s, %s);
"""
TAGS_SELECT_SQL = """
SELECT tag
FROM eats_order_revision.revision_tags
WHERE revision_id = %s;
"""
REVISION_MIXIN_SELECT_SQL = """
SELECT payload
FROM eats_order_revision.revision_mixins
WHERE order_id = %s AND customer_service_id = %s
"""
REVISION_MIXIN_INSERT_SQL = """
INSERT INTO eats_order_revision.revision_mixins (order_id,
                                                 customer_service_id,
                                                 payload)
VALUES (%s, %s, %s);
"""
MIXINS_COUNT_SQL = """
SELECT
    COUNT(*)
FROM eats_order_revision.revision_mixins;
"""
