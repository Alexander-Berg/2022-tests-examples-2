package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t1;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t2;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class TupleElementLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.tupleElement)
                .forArgs(t1(s("")),             un8(1))         .expect(s(""))
                .forArgs(t1(un8(100)),          un8(1))         .expect(un8(100))
                .forArgs(t2(s(""), un8(100)),   un8(1))         .expect(s(""))
                .forArgs(t2(s(""), un8(100)),   un8(2))         .expect(un8(100))
                .build();
    }

}
