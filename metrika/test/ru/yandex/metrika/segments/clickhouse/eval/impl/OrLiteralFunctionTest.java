package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;

public class OrLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.or)
                .forArgs(b(true))                       .expect(b(true))
                .forArgs(b(false))                      .expect(b(false))
                .forArgs(b(true), b(true))              .expect(b(true))
                .forArgs(b(true), b(false))             .expect(b(true))
                .forArgs(b(false), b(true))             .expect(b(true))
                .forArgs(b(false), b(false))            .expect(b(false))

                //vararg
                .forArgs(b(true), b(true), b(true), b(true), b(true))       .expect(b(true))
                .forArgs(b(true), b(true), b(true), b(true), b(false))      .expect(b(true))
                .forArgs(b(false), b(false), b(false), b(false), b(false))  .expect(b(false))
                .build();
    }

}
