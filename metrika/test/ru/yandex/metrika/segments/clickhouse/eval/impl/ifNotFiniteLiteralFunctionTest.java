package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class ifNotFiniteLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @SuppressWarnings({"divzero", "NumericOverflow"})
    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        var inf = 1. / 0.;
        var minusInf = -1. / 0.;

        return new CasesBuilder(CHFunctions.ifNotFinite)
                .forArgs(un8(1), un8(2))        .expect(un8(1))
                .forArgs(un8(1), un16(2))       .expect(un16(1))
                .forArgs(f(inf), un8(0))        .expect(f(0))
                .forArgs(f(inf), f(2))          .expect(f(2))
                .forArgs(f(minusInf), un8(0))   .expect(f(0))
                .forArgs(f(minusInf), f(2))     .expect(f(2))
                .build();
    }

}
