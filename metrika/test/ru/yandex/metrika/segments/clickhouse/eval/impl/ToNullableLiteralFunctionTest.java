package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;

public class ToNullableLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.toNullable)
                .forArgs(s(""))                 .expect(notNull(s("")))
                .forArgs(notNull(s("")))        .expect(notNull(s("")))
                .build();
    }

}
