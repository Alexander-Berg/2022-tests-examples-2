package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t1;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t2;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.FALSE;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.TRUE;

public class NotInLiteralFunctionTest extends ParametrizedLiteralFunctionTest {
    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.notIn)
                .forArgs(un8(1), arr(un8(1)))           .expect(FALSE)
                .forArgs(un8(1), arr(un8(0), un8(1)))   .expect(FALSE)
                .forArgs(un8(1), arr(un8(0), un8(2)))   .expect(TRUE)

                .forArgs(un8(1), t1(un8(1)))            .expect(FALSE)
                .forArgs(un8(1), t2(un8(0), un8(1)))    .expect(FALSE)
                .forArgs(un8(1), t2(un8(0), un8(2)))    .expect(TRUE)
                .build();
    }
}
