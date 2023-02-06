package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;

public class ReinterpretAsUInt32LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.reinterpretAsUInt32)
                .forArgs(s("0"))        .expect(un32(48))
                .forArgs(s("01"))       .expect(un32(48 + 256 * 49))
                .forArgs(s("012"))      .expect(un32(48 + 256 * (49 + 256 * 50)))
                .forArgs(s("0123"))     .expect(un32(48 + 256 * (49 + 256 * (50 + 256 * 51))))
                .forArgs(s("01234"))    .expect(un32(48 + 256 * (49 + 256 * (50 + 256 * 51))))

                .build();
    }

}
