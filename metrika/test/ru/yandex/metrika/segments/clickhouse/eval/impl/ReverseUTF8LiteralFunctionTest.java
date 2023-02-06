package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class ReverseUTF8LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.reverseUTF8)
                .forArgs(s(""))             .expect(s(""))
                .forArgs(s("a"))            .expect(s("a"))
                .forArgs(s("aa"))           .expect(s("aa"))
                .forArgs(s("ab"))           .expect(s("ba"))
                .forArgs(s("aba"))          .expect(s("aba"))
                .forArgs(s("abc"))          .expect(s("cba"))

                // Never odd or even - палиндром
                .forArgs(s("neveroddoreven"))   .expect(s("neveroddoreven"))
                .forArgs(s("привет"))           .expect(s("тевирп"))

                .build();
    }


}
