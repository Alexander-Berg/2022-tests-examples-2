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

public class RoundAgeLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.roundAge)
                .forArgs(un8(0))        .expect(un8(0))
                .forArgs(un16(1))       .expect(un8(17))
                .forArgs(un32(18))      .expect(un8(18))
                .forArgs(un64(24))      .expect(un8(18))
                .forArgs(n8(25))        .expect(un8(25))
                .forArgs(n16(34))       .expect(un8(25))
                .forArgs(n32(35))       .expect(un8(35))
                .forArgs(n32(44))       .expect(un8(35))
                .forArgs(n32(45))       .expect(un8(45))
                .forArgs(n32(54))       .expect(un8(45))
                .forArgs(n32(55))       .expect(un8(55))
                .forArgs(n64(-1))       .expect(un8(0))
                .build();
    }

}
