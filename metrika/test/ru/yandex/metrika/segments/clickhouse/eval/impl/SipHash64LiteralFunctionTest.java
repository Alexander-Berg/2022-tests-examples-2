package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;

public class SipHash64LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.sipHash64)
                .forArgs(s(""))                 .expect(un64("2202906307356721367"))
                .forArgs(s("qqq"))              .expect(un64("17307025126318164505"))
                .forArgs(s("clickhouse"))       .expect(un64("8215640427676154167"))
                .forArgs(s("compiling is fun")) .expect(un64("14632142798108535991"))
                .build();
    }
}
