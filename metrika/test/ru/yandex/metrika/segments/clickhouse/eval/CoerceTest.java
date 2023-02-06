package ru.yandex.metrika.segments.clickhouse.eval;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.types.CHType;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Nullable;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.LiteralFunctions.coerce;


@RunWith(Parameterized.class)
public class CoerceTest<S extends CHType, T extends CHType> {

    @Parameterized.Parameter(0)
    public CHLiteral<S> arg;

    @Parameterized.Parameter(1)
    public T targetType;

    @Parameterized.Parameter(2)
    public CHLiteral<T> expectedResult;

    @Parameterized.Parameter(3)
    public String testName;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return List.of(
                params(un8(1), UInt8(), un8(1)),
                params(un8(1), UInt16(), un16(1)),
                params(un8(1), String(), s("1")),
                params(s("1"), UInt8(), un8(1)),
                params(s("1"), Nullable(String()), notNull(s("1"))),
                params(un8(1), Nullable(String()), notNull(s("1")))
        );
    }

    @Test
    public void test() {
        var res = coerce(arg, targetType);
        assertEquals(expectedResult, res);
    }

    private static <S extends CHType, T extends CHType> Object[] params(CHLiteral<S> arg, T targetType, CHLiteral<T> expectedResult) {
        return new Object[]{arg, targetType, expectedResult, "coerce(" + arg.asSql() + ", " + targetType.getName() + ")"};
    }

}
