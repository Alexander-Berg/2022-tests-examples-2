package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class SubstringUTF8LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.substringUTF8)
                .forArgs(s(""),             un8(1),     un8(2))     .expect(s(""))
                .forArgs(s("test"),         un8(1),     un8(1))     .expect(s("t"))
                .forArgs(s("test"),         un8(1),     un8(2))     .expect(s("te"))
                .forArgs(s("test"),         un8(1),     un8(3))     .expect(s("tes"))
                .forArgs(s("test"),         un8(1),     un8(4))     .expect(s("test"))
                .forArgs(s("test"),         un8(1),     un8(100))   .expect(s("test"))
                .forArgs(s("test"),         un8(10),    un8(100))   .expect(s(""))
                .forArgs(s("привет"),       un8(1),     un8(2))     .expect(s("пр"))
                .build();
    }

}
