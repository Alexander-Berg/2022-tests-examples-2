package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class ConcatLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.concat)
                .forArgs(s("a"),        s(""))             .expect(s("a"))
                .forArgs(s(""),         s("b"))            .expect(s("b"))
                .forArgs(s("a"),        s("b"))            .expect(s("ab"))
                .forArgs(s("click"),    s("house"))        .expect(s("clickhouse"))

                //vararg
                .forArgs(s("a"), s("b"), s("c"), s("d"), s("e"), s("f"), s("g"), s("h"))        .expect(s("abcdefgh"))
                .build();
    }


}
