# -*- coding: utf-8 -*-

from collections import OrderedDict
import textwrap

from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.ydb.declarative.elements import (
    and_,
    Column,
    Function,
    or_,
    Table,
    xor_,
)
from passport.backend.core.ydb.declarative.errors import ProgrammingError
from passport.backend.core.ydb.declarative.query import (
    delete,
    insert,
    select,
)
from passport.backend.core.ydb.declarative.types import (
    Bool,
    Int64,
    Utf8,
)


TEST_BOOL = True
TEST_COLUMN_NAME1 = 'col1'
TEST_COLUMN_NAME2 = 'col2'
TEST_COLUMN_NAME3 = 'col3'
TEST_COLUMN_NAME4 = 'col4'
TEST_FUNC = 'Function'
TEST_INT1 = 1
TEST_INT2 = 2
TEST_NAMESPACE = 'q'
TEST_PARAM_NAME = 'param1'
TEST_TABLE_NAME = 'table1'
TEST_TABLE_NAME2 = 'table2'
TEST_TYPE1 = 'Bool'
TEST_TYPE2 = 'Int64'
TEST_UNICODE = u'тестовая_СТРОКА'


class BaseQueryTest(PassportTestCase):
    def setUp(self):
        self.col1 = Column(TEST_COLUMN_NAME1, Bool, primary_key=True)
        self.col2 = Column(TEST_COLUMN_NAME2, Int64, primary_key=True)
        self.col3 = Column(TEST_COLUMN_NAME3, Utf8)
        self.table = Table(TEST_TABLE_NAME, self.col1, self.col2, self.col3)

    @staticmethod
    def format_query(query):
        return '%s\n' % textwrap.dedent(query).strip('\n')

    def _assert_query_equal(self, query, query2):
        self.assertEqual(self.format_query(query), self.format_query(query2))


class TestSelect(BaseQueryTest):
    def test_simple(self):
        query = select(
            self.table,
            and_(
                self.table.c.col1,
                self.table.c.col2 == TEST_INT1,
                self.col3 == TEST_UNICODE,
            ),
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col2 AS Int64;
            DECLARE $q_col3 AS Utf8;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE table1.col1 AND (table1.col2 = $q_col2) AND (table1.col3 = $q_col3)
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col2': TEST_INT1, '$q_col3': TEST_UNICODE})

    def test_column_list_argument(self):
        query = select(
            [
                self.table.c.col1,
                self.table.c.col2,
            ],
            self.table.c.col1 == TEST_INT1,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col1 AS Bool;
            SELECT table1.col1 AS col1, table1.col2 AS col2
            FROM table1 AS table1
            WHERE table1.col1 = $q_col1
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col1': TEST_BOOL})

    def test_order_by(self):
        query = select(
            self.table,
            self.table.c.col1 == TEST_INT1,
            self.table.c.col2,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col1 AS Bool;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE table1.col1 = $q_col1
            ORDER BY table1.col2
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col1': TEST_BOOL})

    def test_order_by_desc(self):
        query = select(
            self.table,
            self.table.c.col1 == TEST_INT1,
            self.table.c.col2.desc(),
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col1 AS Bool;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE table1.col1 = $q_col1
            ORDER BY table1.col2 DESC
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col1': TEST_BOOL})

    def test_order_by_expression(self):
        query = select(
            self.table,
            self.table.c.col1 == TEST_INT1,
            self.table.c.col2 < TEST_INT1,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col1 AS Bool;
            DECLARE $q_col2 AS Int64;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE table1.col1 = $q_col1
            ORDER BY table1.col2 < $q_col2
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col1': TEST_BOOL, '$q_col2': TEST_INT1})

    def test_group_by(self):
        query = select(
            self.table,
            self.table.c.col1 == TEST_INT1,
        ).group_by(self.table.c.col1)
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col1 AS Bool;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE table1.col1 = $q_col1
            GROUP BY table1.col1
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col1': TEST_BOOL})

    def test_function_argument(self):
        query = select(
            self.table,
            Function(TEST_FUNC, self.table.c.col1) == TEST_INT1,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_function AS Int64;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 AS table1
            WHERE %s(table1.col1) = $q_function
        """ % TEST_FUNC)
        self.assertEqual(compiled.get_parameters(), {'$q_function': TEST_INT1})

    def test_join(self):
        table2 = Table(
            TEST_TABLE_NAME2,
            Column(TEST_COLUMN_NAME3, Int64),
            Column(TEST_COLUMN_NAME4, Utf8),
        )
        query = select(
            [
                self.table.c.col2,
                self.table.c.col3,
                table2,
            ],
            self.table.c.col3 == TEST_UNICODE,
            table2.c.col3,
        ).join(table2, table2.c.col3 == self.table.c.col2)
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            DECLARE $q_col3 AS Utf8;
            SELECT table1.col2 AS col2, table1.col3 AS col3, table2.col3 AS col3_1, table2.col4 AS col4
            FROM table1 AS table1
            JOIN table2 AS table2 ON table2.col3 = table1.col2
            WHERE table1.col3 = $q_col3
            ORDER BY table2.col3
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col3': TEST_UNICODE})

    def test_typed_join(self):
        table2 = Table(
            TEST_TABLE_NAME2,
            Column(TEST_COLUMN_NAME3, Int64),
            Column(TEST_COLUMN_NAME4, Utf8),
        )
        query = select(
            [
                self.table.c.col2,
                table2.c.col3,
            ],
        ).join(table2, table2.c.col3 == self.table.c.col2, 'left outer')
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            SELECT table1.col2 AS col2, table2.col3 AS col3
            FROM table1 AS table1
            LEFT OUTER JOIN table2 AS table2 ON table2.col3 = table1.col2
        """)
        self.assertEqual(compiled.get_parameters(), {})

    def test_complex(self):
        query = select(
            [
                self.table.c.col1,
                self.table.c.col2,
            ],
            or_(
                and_(
                    self.table.c.col1 < TEST_INT1,
                    self.table.c.col2 == TEST_INT2,
                ),
                xor_(
                    self.table.c.col1 == TEST_BOOL,
                    self.table.c.col3 != TEST_UNICODE,
                ),
                or_(
                    (self.table.c.col2 << TEST_INT2) == TEST_INT2,
                    (self.table.c.col2 >= TEST_INT2) == TEST_BOOL,
                    (self.table.c.col2 <= TEST_INT1) == TEST_BOOL,
                ),
                or_(
                    self.table.c.col2.in_((TEST_INT1, TEST_INT2)),
                    self.table.c.col1.is_not_(None),
                ),
            ),
            (
                self.table.c.col1,
                self.table.c.col2.desc(),
            ),
        ).group_by([
            self.table.c.col1,
            self.table.c.col2 > TEST_INT2,
        ])
        compiled = query.compile()
        self._assert_query_equal(
            compiled.get_raw_statement(),
            """
            DECLARE $q_col1 AS Bool;
            DECLARE $q_col2 AS Int64;
            DECLARE $q_col1_1 AS Bool;
            DECLARE $q_col3 AS Utf8;
            DECLARE $q_col2_1 AS Int64;
            DECLARE $q_param AS Int64;
            DECLARE $q_col2_2 AS Int64;
            DECLARE $q_param_1 AS Bool;
            DECLARE $q_col2_3 AS Int64;
            DECLARE $q_param_2 AS Bool;
            DECLARE $q_col2_4 AS Int64;
            DECLARE $q_col2_5 AS Int64;
            DECLARE $q_col2_6 AS Int64;
            SELECT table1.col1 AS col1, table1.col2 AS col2
            FROM table1 AS table1
            WHERE ((table1.col1 < $q_col1) AND (table1.col2 = $q_col2)) """
            """OR ((table1.col1 = $q_col1_1) XOR (table1.col3 != $q_col3)) """
            """OR (((table1.col2 << $q_col2_1) = $q_param) """
            """OR ((table1.col2 >= $q_col2_2) = $q_param_1) """
            """OR ((table1.col2 <= $q_col2_3) = $q_param_2)) """
            """OR ((table1.col2 IN ($q_col2_4, $q_col2_5)) OR (table1.col1 IS NOT NULL))
            ORDER BY table1.col1, table1.col2 DESC
            GROUP BY table1.col1, table1.col2 > $q_col2_6"""
        )
        self.assertEqual(compiled.get_parameters(), {
            '$q_col1': TEST_BOOL,
            '$q_col2': TEST_INT2,
            '$q_col1_1': TEST_BOOL,
            '$q_col3': TEST_UNICODE,
            '$q_col2_1': TEST_INT2,
            '$q_param': TEST_INT2,
            '$q_col2_2': TEST_INT2,
            '$q_param_1': TEST_BOOL,
            '$q_col2_3': TEST_INT1,
            '$q_param_2': TEST_BOOL,
            '$q_col2_4': TEST_INT1,
            '$q_col2_5': TEST_INT2,
            '$q_col2_6': TEST_INT2,
        })

    def test_optimizer_index(self):
        query = select(
            self.table,
            self.table.c.col2 == TEST_INT1,
            optimizer_index='index_1',
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            --!syntax_v1
            DECLARE $q_col2 AS Int64;
            SELECT table1.col1 AS col1, table1.col2 AS col2, table1.col3 AS col3
            FROM table1 view index_1 AS table1
            WHERE table1.col2 = $q_col2
        """)
        self.assertEqual(compiled.get_parameters(), {'$q_col2': TEST_INT1})


class TestInsert(BaseQueryTest):
    def test_simple(self):
        args = OrderedDict()
        args['col2'] = TEST_INT1
        args['col1'] = TEST_BOOL
        args['col3'] = TEST_UNICODE
        query = insert(self.table, args)
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col2 AS Int64;
        DECLARE $col1 AS Bool;
        DECLARE $col3 AS Utf8;
        INSERT INTO table1
        (col2, col1, col3)
        VALUES
        ($col2, $col1, $col3)
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col2': TEST_INT1,
            '$col1': TEST_BOOL,
            '$col3': TEST_UNICODE,
        })

    def test_multiline(self):
        query = insert(self.table).values(
            {
                'col1': TEST_BOOL,
                'col2': TEST_INT1,
                'col3': TEST_UNICODE,
            },
            {
                'col1': False,
                'col2': TEST_INT2,
                'col3': TEST_UNICODE + TEST_UNICODE,
            },
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col1 AS Bool;
        DECLARE $col2 AS Int64;
        DECLARE $col3 AS Utf8;
        DECLARE $col1_1 AS Bool;
        DECLARE $col2_1 AS Int64;
        DECLARE $col3_1 AS Utf8;
        INSERT INTO table1
        (col1, col2, col3)
        VALUES
        ($col1, $col2, $col3),
        ($col1_1, $col2_1, $col3_1)
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col1': TEST_BOOL,
            '$col2': TEST_INT1,
            '$col3': TEST_UNICODE,
            '$col1_1': False,
            '$col2_1': TEST_INT2,
            '$col3_1': TEST_UNICODE + TEST_UNICODE,
        })

    def test_kwargs(self):
        query = insert(self.table).values(
            col1=TEST_BOOL,
            col2=TEST_INT1,
            col3=TEST_UNICODE,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col1 AS Bool;
        DECLARE $col2 AS Int64;
        DECLARE $col3 AS Utf8;
        INSERT INTO table1
        (col1, col2, col3)
        VALUES
        ($col1, $col2, $col3)
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col1': TEST_BOOL,
            '$col2': TEST_INT1,
            '$col3': TEST_UNICODE,
        })

    def test_upsert(self):
        query = insert(self.table, insert_type='UPSERT').values(
            col1=TEST_BOOL,
            col2=TEST_INT1,
            col3=TEST_UNICODE,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col1 AS Bool;
        DECLARE $col2 AS Int64;
        DECLARE $col3 AS Utf8;
        UPSERT INTO table1
        (col1, col2, col3)
        VALUES
        ($col1, $col2, $col3)
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col1': TEST_BOOL,
            '$col2': TEST_INT1,
            '$col3': TEST_UNICODE,
        })

    def test_replace(self):
        query = insert(self.table, insert_type='REPLACE').values(
            col1=TEST_BOOL,
            col2=TEST_INT1,
            col3=TEST_UNICODE,
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col1 AS Bool;
        DECLARE $col2 AS Int64;
        DECLARE $col3 AS Utf8;
        REPLACE INTO table1
        (col1, col2, col3)
        VALUES
        ($col1, $col2, $col3)
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col1': TEST_BOOL,
            '$col2': TEST_INT1,
            '$col3': TEST_UNICODE,
        })


class TestDelete(BaseQueryTest):
    def test_simple(self):
        query = delete(self.table)
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DELETE FROM table1
        """)
        self.assertEqual(compiled.get_parameters(), {})

    def test_where(self):
        query = delete(self.table, self.table.c.col2 == TEST_INT1)
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
        DECLARE $col2 AS Int64;
        DELETE FROM table1
        WHERE col2 = $col2
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col2': TEST_INT1,
        })

    def test_wrong_where(self):
        table2 = Table(TEST_TABLE_NAME2, Column(TEST_COLUMN_NAME4, Int64))
        query = delete(self.table).where(table2.c.col4 == TEST_INT1)
        with self.assertRaises(ProgrammingError):
            query.compile()

    def test_optimizer_index(self):
        query = delete(
            self.table,
            self.table.c.col2 == TEST_INT1,
            optimizer_index='index_1',
        )
        compiled = query.compile()
        self._assert_query_equal(compiled.get_raw_statement(), """
            --!syntax_v1
            DECLARE $col2 AS Int64;
            DELETE FROM table1 ON
            SELECT col1 FROM table1 view index_1
            WHERE col2 = $col2
        """)
        self.assertEqual(compiled.get_parameters(), {
            '$col2': TEST_INT1,
        })

    def test_optimizer_index_no_pk(self):
        table = Table(TEST_TABLE_NAME, Column(TEST_COLUMN_NAME1, Int64))
        with self.assertRaises(ValueError):
            delete(
                table,
                table.c.col1 == TEST_INT1,
                optimizer_index='index_1',
            )
