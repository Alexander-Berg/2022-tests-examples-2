package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class UnhexLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.unhex)
                .forArgs(s("31"))            .expect(s("1"))
                .forArgs(s("636C69636B686F757365"))   .expect(s("clickhouse"))
                .forArgs(s("D0BAD0BBD0B8D0BAD185D0B0D183D181"))     .expect(s("кликхаус"))
                .build();
    }

}
