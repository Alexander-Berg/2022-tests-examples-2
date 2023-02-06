package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;

public class HalfMD5LiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.halfMD5)
                .forArgs(s(""))                 .expect(un64("15284527576400310788"))
                .forArgs(s("qqq"))              .expect(un64("12883223532029570960"))
                .forArgs(s("clickhouse"))       .expect(un64("4085582472856926835"))
                .forArgs(s("compiling is fun")) .expect(un64("3010225429554212933"))
                .build();
    }
}
