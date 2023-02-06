package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class RoundToExp2LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.roundToExp2)
                .forArgs(un8(0))                        .expect(un8(0))
                .forArgs(un8(255))                      .expect(un8(128))
                .forArgs(un16(1))                       .expect(un16(1))
                .forArgs(un16((1 << 16) - 1))           .expect(un16(1 <<  15))
                .forArgs(un32(18))                      .expect(un32(16))
                .forArgs(un32((int) ((1L << 32) - 1)))  .expect(un32((int) ((1L << 31))))
                .forArgs(un64(34))                      .expect(un64(32))
                .forArgs(un64(UInt64().maxValue()))     .expect(un64(1L << 63))

                // https://github.com/ClickHouse/ClickHouse/blob/master/tests/queries/0_stateless/00161_rounding_functions.sql#L45
                .forArgs(f32(25.))                      .expect(f32(16.))
                .forArgs(f32(0.9))                      .expect(f32(0.5))
                .forArgs(f32(0))                        .expect(f32(0))
                .forArgs(f32(-0.5))                     .expect(f32(-0.5))
                .forArgs(f32(-0.6))                     .expect(f32(-0.5))
                .forArgs(f32(-0.2))                     .expect(f32(-0.125))

                // https://github.com/ClickHouse/ClickHouse/blob/master/tests/queries/0_stateless/00161_rounding_functions.sql#L45
                .forArgs(f(25.))                        .expect(f(16.))
                .forArgs(f(0.9))                        .expect(f(0.5))
                .forArgs(f(0))                          .expect(f(0))
                .forArgs(f(-0.5))                       .expect(f(-0.5))
                .forArgs(f(-0.6))                       .expect(f(-0.5))
                .forArgs(f(-0.2))                       .expect(f(-0.125))

                .build();

    }

}
