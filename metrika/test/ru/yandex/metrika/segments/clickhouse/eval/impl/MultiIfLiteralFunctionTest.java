package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class MultiIfLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.multiIf)

                .forArgs(b(true), un8(0), un8(1))  .expect(un8(0))
                .forArgs(b(false), un8(0), un8(1))  .expect(un8(1))

                .forArgs(b(true), s("x"), s("y")).expect(s("x"))
                .forArgs(b(false), s("x"), s("y")).expect(s("y"))
                .forArgs(b(true), s("x"), b(true), s("y"), s("z")).expect(s("x"))
                .forArgs(b(false), s("x"), b(true), s("y"), s("z")).expect(s("y"))

                .forArgs(b(true), s("q"), b(false), s("w"), b(false), s("e"), b(false), s("r"), b(false), s("t"), b(false), s("y"), s("u")).expect(s("q"))
                .forArgs(b(false), s("q"), b(true), s("w"), b(false), s("e"), b(false), s("r"), b(false), s("t"), b(false), s("y"), s("u")).expect(s("w"))
                .forArgs(b(false), s("q"), b(false), s("w"), b(true), s("e"), b(false), s("r"), b(false), s("t"), b(false), s("y"), s("u")).expect(s("e"))
                .forArgs(b(false), s("q"), b(false), s("w"), b(false), s("e"), b(true), s("r"), b(false), s("t"), b(false), s("y"), s("u")).expect(s("r"))
                .forArgs(b(false), s("q"), b(false), s("w"), b(false), s("e"), b(false), s("r"), b(true), s("t"), b(false), s("y"), s("u")).expect(s("t"))
                .forArgs(b(false), s("q"), b(false), s("w"), b(false), s("e"), b(false), s("r"), b(false), s("t"), b(true), s("y"), s("u")).expect(s("y"))
                .forArgs(b(false), s("q"), b(false), s("w"), b(false), s("e"), b(false), s("r"), b(false), s("t"), b(false), s("y"), s("u")).expect(s("u"))

                .build();
    }

}
