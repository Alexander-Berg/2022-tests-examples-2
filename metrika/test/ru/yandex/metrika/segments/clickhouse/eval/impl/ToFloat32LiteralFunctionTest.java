package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.FLOAT_32;
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

public class ToFloat32LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.toFloat32)
                .forArgs(un8(1))                            .expect(f32(1))
                .forArgs(un16(1))                           .expect(f32(1))
                .forArgs(un16(1000))                        .expect(f32(1000))
                .forArgs(un32(1))                           .expect(f32(1))
                .forArgs(un32(100000))                      .expect(f32(100000))
                .forArgs(un64(1))                           .expect(f32(1))
                .forArgs(un64(1L << 40))                    .expect(FLOAT_32.buildLiteral(1099511600000L))
                .forArgs(n8(1))                             .expect(f32(1))
                .forArgs(n8(-10))                           .expect(f32(-10))
                .forArgs(n16(1))                            .expect(f32(1))
                .forArgs(n16(-1000))                        .expect(f32(-1000))
                .forArgs(n16(1000))                         .expect(f32(1000))
                .forArgs(n32(1))                            .expect(f32(1))
                .forArgs(n32(-100000))                      .expect(f32(-100000))
                .forArgs(n32(100000))                       .expect(f32(100000))
                .forArgs(n64(-100500))                      .expect(f32(-100500))
                .forArgs(f32(1))                            .expect(f32(1))
                .forArgs(FLOAT_32.buildLiteral(0.1))        .expect(FLOAT_32.buildLiteral(0.1))
                .forArgs(FLOAT_32.buildLiteral(100.5))      .expect(FLOAT_32.buildLiteral(100.5))
                .forArgs(f(1))                              .expect(f32(1))
                .forArgs(s("1"))                            .expect(f32(1))
                .build();
    }

}
