package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;

public class RoundDurationLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.roundDuration)
                .forArgs(n32(-1))       .expect(un16(0))
                .forArgs(n32(0))        .expect(un16(0))
                .forArgs(n32(1))        .expect(un16(1))
                .forArgs(n32(9))        .expect(un16(1))
                .forArgs(n32(10))       .expect(un16(10))
                .forArgs(n32(29))       .expect(un16(10))
                .forArgs(n32(30))       .expect(un16(30))
                .forArgs(n32(59))       .expect(un16(30))
                .forArgs(n32(60))       .expect(un16(60))
                .forArgs(n32(119))      .expect(un16(60))
                .forArgs(n32(120))      .expect(un16(120))
                .forArgs(n32(179))      .expect(un16(120))
                .forArgs(n32(180))      .expect(un16(180))
                .forArgs(n32(239))      .expect(un16(180))
                .forArgs(n32(240))      .expect(un16(240))
                .forArgs(n32(299))      .expect(un16(240))
                .forArgs(n32(300))      .expect(un16(300))
                .forArgs(n32(599))      .expect(un16(300))
                .forArgs(n32(600))      .expect(un16(600))
                .forArgs(n32(1199))     .expect(un16(600))
                .forArgs(n32(1200))     .expect(un16(1200))
                .forArgs(n32(1799))     .expect(un16(1200))
                .forArgs(n32(1800))     .expect(un16(1800))
                .forArgs(n32(3599))     .expect(un16(1800))
                .forArgs(n32(3600))     .expect(un16(3600))
                .forArgs(n32(7199))     .expect(un16(3600))
                .forArgs(n32(7200))     .expect(un16(7200))
                .forArgs(n32(17999))    .expect(un16(7200))
                .forArgs(n32(18000))    .expect(un16(18000))
                .forArgs(n32(35999))    .expect(un16(18000))
                .forArgs(n32(36000))    .expect(un16(36000))
                .forArgs(n32(100000))   .expect(un16(36000))
                .build();

    }

}
