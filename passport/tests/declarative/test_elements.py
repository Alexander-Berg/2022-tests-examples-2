# -*- coding: utf-8 -*-

from functools import partial

from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.ydb.declarative.elements import (
    and_,
    BinaryExpression,
    BoundParameter,
    Column,
    DescOrderBy,
    Expression,
    Function,
    InListExpression,
    Label,
    NULL,
    OperationsList,
    or_,
    ParametrizableValue,
    SimpleRenderableElement,
    Table,
    UnaryExpression,
    xor_,
)
from passport.backend.core.ydb.declarative.query import RenderContext
from passport.backend.core.ydb.declarative.types import (
    Bool,
    Date,
    Int64,
    Integer,
)
from passport.backend.utils.time import unixtime_to_datetime


TEST_TYPE_NAME = 'Int64'
TEST_BOOL = True
TEST_COLUMN_NAME1 = 'col1'
TEST_COLUMN_NAME2 = 'col2'
TEST_COLUMN_NAME3 = 'col3'
TEST_DATE = unixtime_to_datetime(86400).date()
TEST_DAYS = 1
TEST_FUNCTION_NAME = 'function1'
TEST_INT = 1
TEST_LABEL = 'label1'
TEST_PARAM_PREFIX = 'param'
TEST_PARAM1 = '$q_param'
TEST_STRING1 = 'string1'
TEST_STRING2 = 'string2'
TEST_TABLE_NAME = 'table1'


class BaseTestElements(PassportTestCase):
    def _context(self):
        def get_table_alias(table):
            return self.table_aliases[table.objid]
        return RenderContext('q', get_table_alias, None)

    def setUp(self):
        self.table_aliases = {}
        self.context = self._context()

    def tearDown(self):
        del self.context

    def _assert_binary(self, binary, left, operator, right, postfix=None):
        self.assertIsInstance(binary, BinaryExpression)
        self.assertIs(binary.left, left)
        self.assertIs(binary.right, right)
        self.assertEqual(binary.operator, operator)
        self.assertEqual(binary.postfix, postfix)

    def _assert_binary_bound(self, binary, left, operator, right_val, data_type):
        self.assertIsInstance(binary, BinaryExpression)
        self.assertIs(binary.left, left)
        self.assertEqual(binary.operator, operator)
        self.assertIsInstance(binary.right, ParametrizableValue)
        self.assertEqual(binary.right.param_type, data_type().get_type_annotation())
        self.assertEqual(binary.right.param_prefix, TEST_PARAM_PREFIX)
        self.assertEqual(binary.right.value, right_val)

    def _assert_binary_null(self, binary, left, operator):
        self.assertIsInstance(binary, BinaryExpression)
        self.assertIs(binary.left, left)
        self.assertEqual(binary.operator, operator)
        self.assertIsInstance(binary.right, SimpleRenderableElement)
        self.assertEqual(binary.right.value, 'NULL')

    def _assert_binary_in(self, binary, left, operator, values_list):
        self.assertIsInstance(binary, BinaryExpression)
        self.assertIs(binary.left, left)
        self.assertEqual(binary.operator, operator)
        self.assertIsInstance(binary.right, InListExpression)
        self.assertEqual(binary.right.values, values_list)
        self.assertEqual(binary.right.value_renderer, left._wrap_param)

    def _assert_unary(self, unary, operand, operator):
        self.assertIsInstance(unary, UnaryExpression)
        self.assertIs(unary.operand, operand)
        self.assertIs(unary.operator, operator)

    def _assert_context_empty(self):
        self.assertEqual(self.context.parameters, {})
        self.assertEqual(self.context.parameter_declarations, [])


class TestElements(BaseTestElements):
    def test_simple_renderable_element(self):
        element = SimpleRenderableElement(TEST_PARAM_PREFIX)
        self.assertEqual(element.value, TEST_PARAM_PREFIX)
        self.assertEqual(element._render(self.context), TEST_PARAM_PREFIX)
        self.assertEqual(element.objid, id(element))
        self._assert_context_empty()

    def test_null(self):
        self.assertEqual(NULL._render(self.context), 'NULL')
        self._assert_context_empty()

    def test_parametrizable_value(self):
        element = ParametrizableValue(TEST_PARAM_PREFIX, TEST_INT, TEST_TYPE_NAME)
        self.assertEqual(element.param_prefix, TEST_PARAM_PREFIX)
        self.assertEqual(element.value, TEST_INT)
        self.assertEqual(element.param_type, TEST_TYPE_NAME)
        self.assertEqual(element._render(self.context), TEST_PARAM1)
        self.assertEqual(self.context.parameter_declarations, [(TEST_PARAM1, TEST_TYPE_NAME)])
        self.assertEqual(self.context.parameters, {TEST_PARAM1: TEST_INT})

    def test_bound_parameter(self):
        bound_parameter = BoundParameter(Int64, TEST_BOOL)
        val, type_annotation = bound_parameter._to_param()
        self.assertEqual(val, TEST_INT)
        self.assertEqual(type_annotation, TEST_TYPE_NAME)


class TestExpression(BaseTestElements):
    def test_expression_from_pyval(self):
        expression = Expression()
        val, type_annotation = expression.from_pyval(TEST_DATE)
        self.assertEqual(val, TEST_DAYS)
        self.assertEqual(type_annotation, 'Date')

    def test_expression_overloaded_eq(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression == expression2
        self._assert_binary(binary, expression, '=', expression2)
        binary = expression == TEST_INT
        self._assert_binary_bound(binary, expression, '=', TEST_INT, Int64)

    def test_expression_overloaded_ne(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression != expression2
        self._assert_binary(binary, expression, '!=', expression2)
        binary = expression != TEST_INT
        self._assert_binary_bound(binary, expression, '!=', TEST_INT, Int64)

    def test_expression_overloaded_lt(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression < expression2
        self._assert_binary(binary, expression, '<', expression2)
        binary = expression < TEST_INT
        self._assert_binary_bound(binary, expression, '<', TEST_INT, Int64)

    def test_expression_overloaded_le(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression <= expression2
        self._assert_binary(binary, expression, '<=', expression2)
        binary = expression <= TEST_INT
        self._assert_binary_bound(binary, expression, '<=', TEST_INT, Int64)

    def test_expression_overloaded_gt(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression > expression2
        self._assert_binary(binary, expression, '>', expression2)
        binary = expression > TEST_INT
        self._assert_binary_bound(binary, expression, '>', TEST_INT, Int64)

    def test_expression_overloaded_ge(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression >= expression2
        self._assert_binary(binary, expression, '>=', expression2)
        binary = expression >= TEST_INT
        self._assert_binary_bound(binary, expression, '>=', TEST_INT, Int64)

    def test_expression_overloaded_sum(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression + expression2
        self._assert_binary(binary, expression, '+', expression2)
        binary = expression + TEST_INT
        self._assert_binary_bound(binary, expression, '+', TEST_INT, Int64)

    def test_expression_overloaded_sub(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression - expression2
        self._assert_binary(binary, expression, '-', expression2)
        binary = expression - TEST_INT
        self._assert_binary_bound(binary, expression, '-', TEST_INT, Int64)

    def test_expression_overloaded_mul(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression * expression2
        self._assert_binary(binary, expression, '*', expression2)
        binary = expression * TEST_INT
        self._assert_binary_bound(binary, expression, '*', TEST_INT, Int64)

    def test_expression_overloaded_div(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression / expression2
        self._assert_binary(binary, expression, '/', expression2)
        binary = expression / TEST_INT
        self._assert_binary_bound(binary, expression, '/', TEST_INT, Int64)

    def test_expression_overloaded_mod(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression % expression2
        self._assert_binary(binary, expression, '%', expression2)
        binary = expression % TEST_INT
        self._assert_binary_bound(binary, expression, '%', TEST_INT, Int64)

    def test_expression_overloaded_and(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression & expression2
        self._assert_binary(binary, expression, 'AND', expression2)
        binary = expression & TEST_BOOL
        self._assert_binary_bound(binary, expression, 'AND', TEST_BOOL, Bool)

    def test_expression_overloaded_or(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression | expression2
        self._assert_binary(binary, expression, 'OR', expression2)
        binary = expression | TEST_BOOL
        self._assert_binary_bound(binary, expression, 'OR', TEST_BOOL, Bool)

    def test_expression_overloaded_xor(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression ^ expression2
        self._assert_binary(binary, expression, 'XOR', expression2)
        binary = expression ^ TEST_BOOL
        self._assert_binary_bound(binary, expression, 'XOR', TEST_BOOL, Bool)

    def test_expression_overloaded_not(self):
        expression = Expression()
        unary = ~ expression
        self._assert_unary(unary, expression, 'NOT')

    def test_expression_overloaded_rshift(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression >> expression2
        self._assert_binary(binary, expression, '>>', expression2)
        binary = expression >> TEST_INT
        self._assert_binary_bound(binary, expression, '>>', TEST_INT, Int64)

    def test_expression_overloaded_lshift(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression << expression2
        self._assert_binary(binary, expression, '<<', expression2)
        binary = expression << TEST_INT
        self._assert_binary_bound(binary, expression, '<<', TEST_INT, Int64)

    def test_expression_is(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.is_(expression2)
        self._assert_binary(binary, expression, 'IS', expression2)
        binary = expression.is_(None)
        self._assert_binary_null(binary, expression, 'IS')

    def test_expression_is_not(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.is_not_(expression2)
        self._assert_binary(binary, expression, 'IS NOT', expression2)
        binary = expression.is_not_(None)
        self._assert_binary_null(binary, expression, 'IS NOT')

    def test_expression_like(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.like(expression2)
        self._assert_binary(binary, expression, 'LIKE', expression2)
        binary = expression.like(expression2, False)
        self._assert_binary(binary, expression, 'ILIKE', expression2)
        binary = expression.like(expression2, False, '?')
        self._assert_binary(binary, expression, 'ILIKE', expression2, 'ESCAPE \'?\'')

    def test_expression_concat(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.concat(expression2)
        self._assert_binary(binary, expression, '||', expression2)

    def test_expression_bin_and(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.bin_and_(expression2)
        self._assert_binary(binary, expression, '&', expression2)
        binary = expression.bin_and_(TEST_INT)
        self._assert_binary_bound(binary, expression, '&', TEST_INT, Int64)

    def test_expression_bin_or(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.bin_or_(expression2)
        self._assert_binary(binary, expression, '|', expression2)
        binary = expression.bin_or_(TEST_INT)
        self._assert_binary_bound(binary, expression, '|', TEST_INT, Int64)

    def test_expression_bin_xor(self):
        expression = Expression()
        expression2 = Expression()
        binary = expression.bin_xor_(expression2)
        self._assert_binary(binary, expression, '^', expression2)
        binary = expression.bin_xor_(TEST_INT)
        self._assert_binary_bound(binary, expression, '^', TEST_INT, Int64)

    def test_expression_in(self):
        expression = Expression()
        values_list = [TEST_INT, TEST_INT + 1]
        binary = expression.in_(values_list)
        self._assert_binary_in(binary, expression, 'IN', values_list)

    def test_expression_not_in(self):
        expression = Expression()
        values_list = [TEST_INT, TEST_INT + 1]
        binary = expression.not_in_(values_list)
        self._assert_binary_in(binary, expression, 'NOT IN', values_list)

    def test_expression_desc(self):
        expression = Expression()
        desc = expression.desc()
        self.assertIsInstance(desc, DescOrderBy)
        self.assertIs(desc.expression, expression)


class TestExpressionSubclasses(BaseTestElements):
    def test_function(self):
        arg1 = SimpleRenderableElement(TEST_STRING1)
        arg2 = SimpleRenderableElement(TEST_STRING2)
        function = Function(
            TEST_FUNCTION_NAME,
            arg1,
            arg2,
        )
        self.assertEqual(function.function, TEST_FUNCTION_NAME)
        self.assertEqual(function.args, [arg1, arg2])
        self.assertEqual(
            function._render(self.context),
            '%s(%s, %s)' % (
                TEST_FUNCTION_NAME,
                TEST_STRING1,
                TEST_STRING2,
            ),
        )
        self.assertEqual(function._render(self.context), function._render(self.context, True))
        self.assertEqual(function._extract_columns(), set())
        col = Column(TEST_COLUMN_NAME1, Bool)
        col2 = Column(TEST_COLUMN_NAME1, Bool)
        function = Function(TEST_FUNCTION_NAME, col, col2)
        self.assertEqual(function._extract_columns(), {col, col2})

    def test_unary_expression(self):
        arg = SimpleRenderableElement(TEST_STRING1)
        unary = UnaryExpression(arg, '~')
        self.assertIs(unary.operand, arg)
        self.assertEqual(unary.operator, '~')
        self.assertEqual(unary._render(self.context), '(~ %s)' % TEST_STRING1)
        self.assertEqual(unary._render(self.context, True), '~ %s' % TEST_STRING1)
        self.assertEqual(unary._extract_columns(), set())
        self._assert_context_empty()

        col = Column(TEST_COLUMN_NAME1, Bool)
        unary = UnaryExpression(col, '~')
        self.assertEqual(unary._extract_columns(), {col})

    def test_binary_expression(self):
        arg1 = SimpleRenderableElement(TEST_STRING1)
        arg2 = SimpleRenderableElement(TEST_STRING2)
        binary = BinaryExpression(arg1, arg2, '=')

        self.assertIs(binary.left, arg1)
        self.assertIs(binary.right, arg2)
        self.assertEqual(binary.operator, '=')
        self.assertEqual(
            binary._render(self.context),
            '(%s = %s)' % (TEST_STRING1, TEST_STRING2),
        )
        self.assertEqual(
            binary._render(self.context, True),
            '%s = %s' % (TEST_STRING1, TEST_STRING2),
        )
        self._assert_context_empty()

        col = Column(TEST_COLUMN_NAME1, Bool)
        binary = BinaryExpression(arg1, col, '=')
        self.assertEqual(binary._extract_columns(), {col})
        col2 = Column(TEST_COLUMN_NAME2, Bool)
        binary = BinaryExpression(col, col2, '=')
        self.assertEqual(binary._extract_columns(), {col, col2})
        self._assert_context_empty()

    def test_in_list_expression(self):
        arg1 = TEST_DATE
        arg2 = None
        arg3 = UnaryExpression(SimpleRenderableElement(TEST_STRING1), '~')
        expression = Expression()
        values = [arg1, arg2, arg3]
        in_list = InListExpression(values, expression._wrap_param)
        self.assertEqual(in_list.values, values)
        self.assertEqual(in_list.value_renderer, expression._wrap_param)
        expected = '(%s, NULL, (~ %s))' % (TEST_PARAM1, TEST_STRING1)
        self.assertEqual(in_list._render(self.context), expected)
        self.context = self._context()
        self.assertEqual(in_list._render(self.context, True), expected)
        self.assertEqual(self.context.parameters, {TEST_PARAM1: TEST_DAYS})

    def test_operations_list(self):
        expression1 = SimpleRenderableElement(TEST_COLUMN_NAME1)
        expression2 = SimpleRenderableElement(TEST_COLUMN_NAME2)
        expression3 = SimpleRenderableElement(TEST_COLUMN_NAME3)
        values = (expression1, expression2, expression3)
        columns = (TEST_COLUMN_NAME1, TEST_COLUMN_NAME2, TEST_COLUMN_NAME3)
        operations_list = OperationsList(
            values,
            'AND'
        )
        self.assertEqual(operations_list.values, values)
        self.assertEqual(operations_list.operator, 'AND')
        self.assertEqual(
            operations_list._render(self.context),
            '(%s AND %s AND %s)' % columns,
        )
        self.assertEqual(
            operations_list._render(self.context, True),
            '%s AND %s AND %s' % columns,
        )
        self.assertEqual(
            and_(expression1, expression2, expression3)._render(self.context),
            '(%s AND %s AND %s)' % columns,
        )
        self.assertEqual(
            or_(expression1, expression2, expression3)._render(self.context),
            '(%s OR %s OR %s)' % columns,
        )
        self.assertEqual(
            xor_(expression1, expression2, expression3)._render(self.context),
            '(%s XOR %s XOR %s)' % columns,
        )

    def test_desc(self):
        arg = SimpleRenderableElement(TEST_COLUMN_NAME1)
        desc = DescOrderBy(arg)
        self.assertIs(desc.expression, arg)
        self.assertEqual(desc._render(self.context), '%s DESC' % TEST_COLUMN_NAME1)
        self.assertEqual(desc._render(self.context), desc._render(self.context, True))
        self.assertEqual(desc._extract_columns(), set())

        col = Column(TEST_COLUMN_NAME1, Bool)
        desc = DescOrderBy(col)
        self.assertEqual(desc._extract_columns(), {col})


class TestSchema(BaseTestElements):
    def test_table(self):
        col1 = Column(TEST_COLUMN_NAME1, Bool, primary_key=True)
        col2 = Column(TEST_COLUMN_NAME2, Int64, primary_key=True)
        col3 = Column(TEST_COLUMN_NAME3, Int64)
        table = Table(TEST_TABLE_NAME, col1, col2, col3)

        self.assertEqual(table.name, TEST_TABLE_NAME)
        self.assertEqual(table.column_dict, {
            TEST_COLUMN_NAME1: col1,
            TEST_COLUMN_NAME2: col2,
            TEST_COLUMN_NAME3: col3,
        })
        self.assertEqual(table._extract_columns(), [col1, col2, col3])
        self.assertEqual(getattr(table.c, TEST_COLUMN_NAME1), col1)
        self.assertEqual(getattr(table.c, TEST_COLUMN_NAME2), col2)
        self.assertEqual(getattr(table.c, TEST_COLUMN_NAME3), col3)
        self.assertIs(col1.table, table)
        self.assertIs(col2.table, table)
        self.assertIs(col3.table, table)
        self.assertEqual(table.primary_key, {
            TEST_COLUMN_NAME1: col1,
            TEST_COLUMN_NAME2: col2,
        })
        self.assertEqual(table.first_primary_key, col1)
        self.assertEqual(table.first_primary_key_name, TEST_COLUMN_NAME1)
        self.assertEqual(table._render(self.context), TEST_TABLE_NAME)
        self.assertEqual(table._render(self.context), table._render(self.context, True))
        self._assert_context_empty()

    def test_table_no_primary_keys(self):
        col1 = Column(TEST_COLUMN_NAME1, Bool)
        col2 = Column(TEST_COLUMN_NAME2, Int64)
        col3 = Column(TEST_COLUMN_NAME3, Int64)
        table = Table(TEST_TABLE_NAME, col1, col2, col3)
        self.assertEqual(table.primary_key, {})
        self.assertIsNone(table.first_primary_key)
        self.assertIsNone(table.first_primary_key_name)

    def test_column(self):
        col = Column(TEST_COLUMN_NAME1, Bool(), True)
        self.assertEqual(col.name, TEST_COLUMN_NAME1)
        self.assertIsNone(col.table)
        self.assertIsInstance(col.data_type, Bool)
        self.assertTrue(col.primary_key)

        table = Table(TEST_TABLE_NAME, col)
        self.table_aliases[table.objid] = table.name
        self.assertIs(col.table, table)

        self.assertEqual(col.from_pyval(TEST_INT), (TEST_BOOL, 'Bool'))
        self.assertEqual(col.to_pyval(TEST_BOOL), TEST_BOOL)
        self.assertEqual(col._get_param_prefix(), TEST_COLUMN_NAME1)
        self.assertEqual(
            col._render(self.context),
            '%s.%s' % (TEST_TABLE_NAME, TEST_COLUMN_NAME1),
        )

    def test_column_data_type_class_only(self):
        col = Column(TEST_COLUMN_NAME1, Bool)
        self.assertIsInstance(col.data_type, Bool)

    def test_column_data_type_parameters(self):
        col = Column(TEST_COLUMN_NAME1, Integer(32, False))
        self.assertIsInstance(col.data_type, Integer)
        self.assertEqual(col.data_type.size, 32)
        self.assertFalse(col.data_type.signed)

    def test_column_data_type_partial(self):
        col = Column(TEST_COLUMN_NAME1, partial(Integer, 32))
        self.assertIsInstance(col.data_type, Integer)
        self.assertEqual(col.data_type.size, 32)
        self.assertEqual(col.data_type.signed, Integer().signed)

    def test_label(self):
        col1 = Column(TEST_COLUMN_NAME1, Bool)

        label = col1.label(TEST_LABEL)
        self.assertIsInstance(label, Label)
        self.assertIs(label.element, col1)
        self.assertEqual(label.name, TEST_LABEL)

    def test_type_converting_chain(self):
        col1 = Column(TEST_COLUMN_NAME1, Date)

        self.assertEqual(col1.from_pyval(TEST_DATE), (TEST_DAYS, 'Date'))
        self.assertEqual(col1.to_pyval(TEST_DAYS), TEST_DATE)
