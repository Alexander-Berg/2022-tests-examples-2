package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;

public class IntHash32LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.intHash32)
                .forArgs(un64("574508571422434564"))    .expect(un32("1232799698"))
                .forArgs(un64("5353047191450705463"))   .expect(un32("2109475228"))
                .forArgs(un64("8760395861444360944"))   .expect(un32("2571454567"))
                .forArgs(un64("653719901417520498"))    .expect(un32("13401587"))
                .build();
    }
}
