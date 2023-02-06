package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dt;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class ToHourLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.toHour)
                .forArgs(dt("2091-04-22 11:19:56")).expect(un8(11))
                .forArgs(dt("2035-01-08 17:01:50")).expect(un8(17))
                .forArgs(dt("2003-10-20 14:49:13")).expect(un8(14))
                .forArgs(dt("2011-05-01 11:31:51")).expect(un8(11))
                .forArgs(dt("1980-12-20 21:38:37")).expect(un8(21))
                .forArgs(dt("1979-09-14 01:03:56")).expect(un8(1))
                .forArgs(dt("2098-07-24 19:43:50")).expect(un8(19))
                .forArgs(dt("2026-09-02 06:23:09")).expect(un8(6))
                .forArgs(dt("1996-11-02 02:27:59")).expect(un8(2))
                .forArgs(dt("2055-03-24 11:55:46")).expect(un8(11))
                .build();
    }

}
