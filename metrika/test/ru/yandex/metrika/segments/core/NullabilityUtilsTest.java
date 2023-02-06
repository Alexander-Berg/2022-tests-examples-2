package ru.yandex.metrika.segments.core;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.eval.compile.ExpressionEvaluator;
import ru.yandex.metrika.segments.clickhouse.literals.CHBoolean;
import ru.yandex.metrika.segments.clickhouse.literals.CHDate;
import ru.yandex.metrika.segments.clickhouse.literals.CHNull;
import ru.yandex.metrika.segments.clickhouse.types.TString;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Equals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.If;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.and;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ifNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.isNotNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.isNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.or;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateOrNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toNullable;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt32OrNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.core.NullabilityUtils.asNullable;
import static ru.yandex.metrika.segments.core.NullabilityUtils.isNullable;
import static ru.yandex.metrika.segments.core.NullabilityUtils.nullSafeEquals;
import static ru.yandex.metrika.segments.core.NullabilityUtils.nullSafeNotEquals;

public class NullabilityUtilsTest {

    @Test
    public void isNullableSimple1() {
        assertNullable(toDateOrNull(s("")));
    }

    @Test
    public void isNullableSimple2() {
        assertNullable(and(toDateOrNull(s("")).eq(toNullable(CHDate.ZERO)), un32(1).gt(un32(0))));
    }

    @Test
    public void isNullableSimple3() {
        assertNotNullable(If(toDateOrNull(s("")).eq(toNullable(CHDate.ZERO)), un32(1), un32(0)));
    }

    @Test
    public void isNullableSimple4() {
        assertNullable(If(toDateOrNull(s("")).eq(toNullable(CHDate.ZERO)), toNullable(un32(1)), toUInt32OrNull(s(""))));
    }

    @Test
    public void isNullableSimple5() {
        assertNotNullable(ifNull(toDateOrNull(s("")), CHDate.ZERO));
    }

    @Test
    public void isNullableComplex1() {
        assertNotNullable(isNull(If(toDateOrNull(s("")).eq(toNullable(CHDate.ZERO)), toNullable(un32(1)), toUInt32OrNull(s("")))));
    }

    @Test
    public void isNullableComplex2() {
        assertNullable(or(
                isNull(If(toDateOrNull(s("")).eq(toNullable(CHDate.ZERO)), toNullable(un32(1)), toUInt32OrNull(s("")))),
                toNullable(un32(1)).ge(toNullable(un32(0)))
        ));
    }

    @Test
    public void nullSafeEquals1() {
        var l = s("l"); // not nullable
        var r = s("r"); // not nullable
        var res = nullSafeEquals(l, r);
        assertEquals(Equals(l, r), res);
        assertFalseExpression(res);
    }

    @Test
    public void nullSafeEquals2() {
        var l = asNullable(s("l")); // not really nullable, just type cast
        var r = toNullable(s("r")); // really nullable
        var res = nullSafeEquals(l, r);
        assertEquals(ifNull(asNullable(Equals(l, r)), b(false)), res);
        assertFalseExpression(res);

        var resViceVersa = nullSafeEquals(r, l);
        assertEquals(ifNull(asNullable(Equals(r, l)), b(false)), resViceVersa);
        assertFalseExpression(resViceVersa);
    }

    @Test
    public void nullSafeEquals3() {
        var l = toNullable(s("l")); // really nullable
        var r = toNullable(s("r")); // really nullable
        var res = nullSafeEquals(l, r);
        assertEquals(or(and(isNull(l), isNull(r)), ifNull(asNullable(Equals(l, r)), b(false))), res);
        assertFalseExpression(res);
    }

    @Test
    public void nullSafeNotEquals1() {
        var l = s("l"); // not nullable
        var r = s("r"); // not nullable
        var res = nullSafeNotEquals(l, r);
        assertEquals(notEquals(l, r), res);
        assertTrueExpression(res);
    }

    @Test
    public void nullSafeNotEquals2() {
        var l = asNullable(s("l")); // not really nullable, just type cast
        var r = toNullable(s("r")); // really nullable
        var res = nullSafeNotEquals(l, r);
        assertEquals(ifNull(asNullable(notEquals(l, r)), b(true)), res);
        assertTrueExpression(res);

        var resViceVersa = nullSafeNotEquals(r, l);
        assertEquals(ifNull(asNullable(notEquals(r, l)), b(true)), resViceVersa);
        assertTrueExpression(resViceVersa);
    }

    @Test
    public void nullSafeNotEquals3() {
        var l = toNullable(s("l")); // really nullable
        var r = toNullable(s("r")); // really nullable
        var res = nullSafeNotEquals(l, r);
        assertEquals(or(or(and(isNull(l), isNotNull(r)), and(isNotNull(l), isNull(r))), ifNull(asNullable(notEquals(l, r)), b(false))), res);
        assertTrueExpression(res);
    }

    @Test
    public void nullSafeEqualsSanityCheck() {
        assertTrueExpression(nullSafeEquals(nullStr(), nullStr()));
        assertTrueExpression(nullSafeEquals(s("x"), s("x")));
        assertTrueExpression(nullSafeEquals(toNullable(s("x")), toNullable(s("x"))));

        assertFalseExpression(nullSafeEquals(asNullable(s("x")), nullStr()));
        assertFalseExpression(nullSafeEquals(nullStr(), asNullable(s("x"))));
        assertFalseExpression(nullSafeEquals(s("x"), s("y")));
        assertFalseExpression(nullSafeEquals(toNullable(s("x")), toNullable(s("y"))));
    }

    @Test
    public void nullSafeNotEqualsSanityCheck() {
        assertFalseExpression(nullSafeNotEquals(nullStr(), nullStr()));
        assertFalseExpression(nullSafeNotEquals(s("x"), s("x")));
        assertFalseExpression(nullSafeNotEquals(toNullable(s("x")), toNullable(s("x"))));

        assertTrueExpression(nullSafeNotEquals(asNullable(s("x")), nullStr()));
        assertTrueExpression(nullSafeNotEquals(nullStr(), asNullable(s("x"))));
        assertTrueExpression(nullSafeNotEquals(s("x"), s("y")));
        assertTrueExpression(nullSafeNotEquals(toNullable(s("x")), toNullable(s("y"))));
    }

    private static void assertNullable(Expression<?> expression) {
        assertTrue(isNullable(expression));
    }

    private static void assertNotNullable(Expression<?> expression) {
        assertFalse(isNullable(expression));
    }

    private static void assertTrueExpression(Expression<?> expression) {
        var res = ExpressionEvaluator.staticEval(expression);
        assertEquals("Expected expression " + expression + " to be true but was " + res, CHBoolean.TRUE, res);
    }

    private static void assertFalseExpression(Expression<?> expression) {
        var res = ExpressionEvaluator.staticEval(expression);
        assertEquals("Expected expression " + expression + " to be false but was " + res, CHBoolean.FALSE, res);
    }

    private static CHNull<TString> nullStr() {
        return new CHNull<>(String());
    }

}
