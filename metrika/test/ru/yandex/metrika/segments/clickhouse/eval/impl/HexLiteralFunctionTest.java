package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.unhex;

public class HexLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.hex)
                .forArgs(s("1"))            .expect(s("31"))
                .forArgs(s("clickhouse"))   .expect(s("636C69636B686F757365"))
                .forArgs(s("кликхаус"))     .expect(s("D0BAD0BBD0B8D0BAD185D0B0D183D181"))
                .forArgs(unhex("00000000000000000000FFFF"))     .expect(s("00000000000000000000FFFF"))
                .build();
    }

}
