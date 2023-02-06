package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;
import ru.yandex.metrika.segments.clickhouse.literals.CHBoolean;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Boolean;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Null;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class IfLiteralFunctionTest extends ParametrizedLiteralFunctionTest{

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.If)
                .forArgs(CHBoolean.TRUE, s("yes"), s("no")).expect(s("yes"))
                .forArgs(CHBoolean.FALSE, s("yes"), s("no")).expect(s("no"))
                .forArgs(CHBoolean.TRUE, un32(1), un64(2)).expect(un64(1))
                .forArgs(CHBoolean.TRUE, un8(1), n32(0)).expect(n32(1))
                .forArgs(Null(Boolean()), un8(1), n32(0)).expect(n32(0))
                .build();
    }
}
