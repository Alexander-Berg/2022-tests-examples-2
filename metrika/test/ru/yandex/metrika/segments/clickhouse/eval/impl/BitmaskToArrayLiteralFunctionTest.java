package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;

public class BitmaskToArrayLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.bitmaskToArray)
                .forArgs(un8(1))    .expect(arr(un8(1)))
                .forArgs(un8(2))    .expect(arr(un8(2)))
                .forArgs(un8(3))    .expect(arr(un8(1), un8(2)))
                .forArgs(un8(100))  .expect(arr(un8(4), un8(32), un8(64)))
                .forArgs(un16(1000)).expect(arr(un16(8), un16(32), un16(64), un16(128), un16(256), un16(512)))
                .forArgs(n8(-10))   .expect(arr(n8(2), n8(4), n8(16), n8(32), n8(64), n8(-128)))
                .build();
    }
}
