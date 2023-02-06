package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class ReinterpretAsStringLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.reinterpretAsString)
                .forArgs(un8(48))                                       .expect(s("0"))
                .forArgs(un16(48))                                      .expect(s("0"))
                .forArgs(un32(48))                                      .expect(s("0"))
                .forArgs(un64(48))                                      .expect(s("0"))
                .forArgs(un16(48 + 256 * 49))                           .expect(s("01"))
                .forArgs(un32(48 + 256 * 49))                           .expect(s("01"))
                .forArgs(un64(48 + 256 * 49))                           .expect(s("01"))
                .forArgs(un32(48 + 256 * (49 + 256 * 50)))              .expect(s("012"))
                .forArgs(un64(48 + 256 * (49 + 256 * 50)))              .expect(s("012"))
                .forArgs(un64(48 + 256 * (49 + 256 * (50 + 256 * 51)))) .expect(s("0123"))

                .build();
    }

}
