package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.FALSE;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.TRUE;

public class HasLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.has)
                .forArgs(arr(un8(1)),           un8(1))   .expect(TRUE)
                .forArgs(arr(un8(0), un8(1)),   un8(1))   .expect(TRUE)
                .forArgs(arr(un8(0), un8(2)),   un8(1))   .expect(FALSE)
                .build();
    }
}
