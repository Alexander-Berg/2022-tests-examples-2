package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class IntDivLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.intDiv)
                .forArgs(   un8(7),     un8(3))       .expect(un8(2))
                .forArgs(   un16(11),   un16(2))      .expect(un16(5))
                .forArgs(   un32(100),  un32(33))     .expect(un32(3))
                .forArgs(   un64(21),   un64(10))     .expect(un64(2))
                .forArgs(   n8(-100),   n8(22))       .expect(n8(-4))
                .forArgs(   n16(17),    n16(4))       .expect(n16(4))
                .forArgs(   n32(1),     n32(1))       .expect(n32(1))
                .forArgs(   n64(8),     n64(7))       .expect(n64(1))
                .build();
    }

}
