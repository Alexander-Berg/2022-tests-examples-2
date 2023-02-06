package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;
import ru.yandex.metrika.util.Patterns;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.FALSE;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.TRUE;

public class MatchLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.match)
                .forArgs(s(""), s("b"))         .expect(FALSE)
                .forArgs(s("a"), s("b"))        .expect(FALSE)
                .forArgs(s("b"), s("b"))        .expect(TRUE)
                .forArgs(s("a"), s("."))        .expect(TRUE)

                .forArgs(s("lavrinovich@yandex-team.ru"),   s(Patterns.EMAIL.pattern()))  .expect(TRUE)
                .forArgs(s("clearly#not@an_email??"),       s(Patterns.EMAIL.pattern()))  .expect(FALSE)

                .forArgs(s("1234321"), s("\\d+"))           .expect(TRUE)
                .forArgs(s("12aa21"),  s("\\d+"))           .expect(TRUE)
                .forArgs(s("12aa21"),  s("\\d{3,}"))        .expect(FALSE)
                .forArgs(s("123aa21"), s("\\d{3,}"))        .expect(TRUE)
                .forArgs(s("123aa21"), s("1\\d{2,}"))       .expect(TRUE)


                .forArgs(s("something"), s("thin"))         .expect(TRUE)
                .forArgs(s("something"), s("th.n"))         .expect(TRUE)
                .forArgs(s("something"), s("th.nk"))        .expect(FALSE)

                .build();
    }

}
