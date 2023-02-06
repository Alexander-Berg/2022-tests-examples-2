package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Null;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class IfNullLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.ifNull)
                .forArgs(un8(1), un8(2))            .expect(un8(1))
                .forArgs(s("a"), s("b"))            .expect(s("a"))

                .forArgs(notNull(un8(1)), un8(2))   .expect(un8(1))
                .forArgs(notNull(un8(1)), un16(2))  .expect(un16(1))
                .forArgs(notNull(s("a")), s("b"))   .expect(s("a"))

                .forArgs(Null(UInt8()), un8(2))     .expect(un8(2))
                .forArgs(Null(UInt8()), un16(2))    .expect(un16(2))
                .forArgs(Null(String()), s("b"))    .expect(s("b"))

                .forArgs(Null(UInt8()), notNull(un8(2)))    .expect(notNull(un8(2)))
                .forArgs(Null(UInt8()), notNull(un16(2)))   .expect(notNull(un16(2)))
                .forArgs(Null(String()), notNull(s("b")))   .expect(notNull(s("b")))

                .forArgs(Null(UInt8()), Null(UInt8()))      .expect(Null(UInt8()))
                .forArgs(Null(UInt8()), Null(UInt16()))     .expect(Null(UInt16()))
                .forArgs(Null(String()), Null(String()))    .expect(Null(String()))
                .build();
    }
}
