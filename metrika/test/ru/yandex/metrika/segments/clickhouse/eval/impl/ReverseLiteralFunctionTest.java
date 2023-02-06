package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.unhex;

public class ReverseLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.reverse)
                .forArgs(s(""))             .expect(s(""))
                .forArgs(s("a"))            .expect(s("a"))
                .forArgs(s("aa"))           .expect(s("aa"))
                .forArgs(s("ab"))           .expect(s("ba"))
                .forArgs(s("aba"))          .expect(s("aba"))
                .forArgs(s("abc"))          .expect(s("cba"))

                // Never odd or even - палиндром
                .forArgs(s("neveroddoreven"))   .expect(s("neveroddoreven"))
                .forArgs(s("привет"))           .expect(unhex("82D1B5D0B2D0B8D080D1BFD0"))

                .build();
    }


}
