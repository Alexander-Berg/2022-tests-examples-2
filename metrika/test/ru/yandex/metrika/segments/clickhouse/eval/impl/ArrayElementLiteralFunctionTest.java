package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.emptyArr;

public class ArrayElementLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.arrayElement)

                .forArgs(emptyArr(UInt8()),     un8(0))     .expect(un8(0))
                .forArgs(arr(un8(7)),           un8(1))     .expect(un8(7))
                .forArgs(arr(un8(7), un8(8)),   un8(1))     .expect(un8(7))
                .forArgs(arr(un8(7), un8(8)),   un8(2))     .expect(un8(8))
                .forArgs(arr(un8(7), un8(8)),   un8(100))   .expect(un8(0))

                .forArgs(arr(un8(7), un8(8)),   n8(-1))     .expect(un8(8))
                .forArgs(arr(un8(7), un8(8)),   n8(-2))     .expect(un8(7))
                .forArgs(arr(un8(7), un8(8)),   n8(-100))   .expect(un8(0))

                .forArgs(emptyArr(String()),    un8(0))     .expect(s(""))
                .forArgs(arr(s("a"), s("b")),   un8(1))     .expect(s("a"))
                .forArgs(arr(s("a"), s("b")),   un8(2))     .expect(s("b"))
                .forArgs(arr(s("a"), s("b")),   un8(100))   .expect(s(""))

                .build();
    }
}
