import dataclasses


INSERT_PRODUCT_FEEDBACK = """
INSERT INTO products_feedback.feedback (
    yandex_uid,
    product_id,
    score,
    comment
)
VALUES (
    %s,
    %s,
    %s,
    %s
)
"""

SELECT_PRODUCT_FEEDBACK = """
SELECT
    yandex_uid,
    product_id,
    score,
    comment
FROM products_feedback.feedback
WHERE yandex_uid = %s
"""

COUNT_ENTRIES = """
SELECT COUNT(*) FROM products_feedback.feedback
"""


@dataclasses.dataclass
class ProductFeedback:
    def __init__(self, pgsql, yandex_uid, product_id, score, comment=None):
        self.pg_sql = pgsql['grocery_products_feedback']
        self.yandex_uid = yandex_uid
        self.product_id = product_id
        self.score = score
        self.comment = comment

    def update_db(self):
        cursor = self.pg_sql.cursor()
        cursor.execute(
            INSERT_PRODUCT_FEEDBACK,
            [self.yandex_uid, self.product_id, self.score, self.comment],
        )

    def compare_with_db(self):
        cursor = self.pg_sql.cursor()

        cursor.execute(SELECT_PRODUCT_FEEDBACK, [self.yandex_uid])
        result = cursor.fetchone()
        assert result
        (yandex_uid, product_id, score, comment) = result

        assert self.yandex_uid == yandex_uid
        assert self.product_id == product_id
        assert self.score == score
        assert self.comment == comment

    def check_entires_count(self, expected_count):
        cursor = self.pg_sql.cursor()

        cursor.execute(COUNT_ENTRIES)
        result = cursor.fetchone()

        assert result

        assert int(expected_count) == int(*result)
