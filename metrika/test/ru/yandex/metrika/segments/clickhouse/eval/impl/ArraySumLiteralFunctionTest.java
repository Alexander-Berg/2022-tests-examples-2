package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Float64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.emptyArr;

public class ArraySumLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.arraySum)
                .forArgs(emptyArr(UInt8()))             .expect(un64(0))
                .forArgs(arr(un8(0)))                   .expect(un64(0))
                .forArgs(arr(un8(0), un8(1)))           .expect(un64(1))
                .forArgs(arr(un8(0), un8(1), un8(2)))   .expect(un64(3))

                .forArgs(emptyArr(Int8()))              .expect(n64(0))
                .forArgs(arr(n8(0)))                    .expect(n64(0))
                .forArgs(arr(n8(0), n8(1)))             .expect(n64(1))
                .forArgs(arr(n8(0), n8(1), n8(2)))      .expect(n64(3))

                .forArgs(emptyArr(Float64()))           .expect(f(0))
                .forArgs(arr(f(0.1)))                   .expect(f(0.1))
                .forArgs(arr(f(0.1), f(1.2)))           .expect(f(0.1 + 1.2))
                .forArgs(arr(f(0.1), f(1.2), f(2.3)))   .expect(f(0.1 + 1.2 + 2.3))
                .build();
    }
}
