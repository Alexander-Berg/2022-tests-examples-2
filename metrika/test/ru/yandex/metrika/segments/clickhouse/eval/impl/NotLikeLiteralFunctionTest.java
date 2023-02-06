package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.FALSE;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.TRUE;

public class NotLikeLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.notLike)
                .forArgs(s(""), s("b"))         .expect(TRUE)
                .forArgs(s("a"), s("b"))        .expect(TRUE)
                .forArgs(s("b"), s("b"))        .expect(FALSE)
                .forArgs(s("a"), s("_"))        .expect(FALSE)

                .forArgs(s("something"), s("thin"))         .expect(TRUE)
                .forArgs(s("something"), s("%thin%"))       .expect(FALSE)
                .forArgs(s("something"), s("th_n"))         .expect(TRUE)
                .forArgs(s("something"), s("%th_n%"))       .expect(FALSE)
                .forArgs(s("something"), s("%th_nk%"))      .expect(TRUE)

                .forArgs(s("something"), s("so%ng"))        .expect(FALSE)

                .forArgs(s("1%1"), s("_%%_"))        .expect(FALSE)


                .build();
    }

}
