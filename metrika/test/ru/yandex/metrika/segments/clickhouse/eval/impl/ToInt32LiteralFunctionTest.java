package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class ToInt32LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.toInt32)
                .forArgs(un8(1))        .expect(n32(1))
                .forArgs(un16(1))       .expect(n32(1))
                .forArgs(un16(1000))    .expect(n32(1000))
                .forArgs(un32(1))       .expect(n32(1))
                .forArgs(un32(100000))  .expect(n32(100000))
                .forArgs(un64(1))       .expect(n32(1))
                .forArgs(un64(1L << 40)).expect(n32(0))
                .forArgs(n8(1))         .expect(n32(1))
                .forArgs(n8(-10))       .expect(n32(-10))
                .forArgs(n16(1))        .expect(n32(1))
                .forArgs(n16(-1000))    .expect(n32(-1000))
                .forArgs(n16(1000))     .expect(n32(1000))
                .forArgs(n32(1))        .expect(n32(1))
                .forArgs(n32(-100000))  .expect(n32(-100000))
                .forArgs(n32(100000))   .expect(n32(100000))
                .forArgs(n64(-100500))  .expect(n32(-100500))
                .forArgs(f32(1))        .expect(n32(1))
                .forArgs(f32(0.1))      .expect(n32(0))
                .forArgs(f32(100.5))    .expect(n32(100))
                .forArgs(f(1))          .expect(n32(1))
                .forArgs(s("1"))        .expect(n32(1))
                .build();
    }

}
