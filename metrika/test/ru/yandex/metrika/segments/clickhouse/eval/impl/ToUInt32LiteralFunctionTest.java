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

public class ToUInt32LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.toUInt32)
                .forArgs(un8(1))        .expect(un32(1))
                .forArgs(un16(1))       .expect(un32(1))
                .forArgs(un16(1000))    .expect(un32(1000))
                .forArgs(un32(1))       .expect(un32(1))
                .forArgs(un32(100000))  .expect(un32(100000))
                .forArgs(un64(1))       .expect(un32(1))
                .forArgs(un64(1L << 40)).expect(un32(0))
                .forArgs(n8(1))         .expect(un32(1))
                .forArgs(n8(-10))       .expect(un32(Integer.parseUnsignedInt("4294967286")))
                .forArgs(n16(1))        .expect(un32(1))
                .forArgs(n16(-1000))    .expect(un32(Integer.parseUnsignedInt("4294966296")))
                .forArgs(n16(1000))     .expect(un32(1000))
                .forArgs(n32(1))        .expect(un32(1))
                .forArgs(n32(-100000))  .expect(un32(Integer.parseUnsignedInt("4294867296")))
                .forArgs(n32(100000))   .expect(un32(100000))
                .forArgs(n64(-100500))  .expect(un32(Integer.parseUnsignedInt("4294866796")))
                .forArgs(f32(1))        .expect(un32(1))
                .forArgs(f32(0.1))      .expect(un32(0))
                .forArgs(f32(100.5))    .expect(un32(100))
                .forArgs(f(1))          .expect(un32(1))
                .forArgs(s("1"))        .expect(un32(1))
                .build();
    }

}
