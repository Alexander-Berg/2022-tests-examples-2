package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;
import ru.yandex.metrika.segments.clickhouse.literals.CHBoolean;
import ru.yandex.metrika.segments.clickhouse.literals.CHNull;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Null;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class IsNullLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.isNull)
                .forArgs(un8(1))                    .expect(CHBoolean.FALSE)
                .forArgs(notNull(un8(1)))           .expect(CHBoolean.FALSE)
                .forArgs(s(""))                     .expect(CHBoolean.FALSE)
                .forArgs(notNull(s("")))            .expect(CHBoolean.FALSE)
                .forArgs(CHNull.instance)           .expect(CHBoolean.TRUE)
                .forArgs(Null(UInt8()))             .expect(CHBoolean.TRUE)
                .forArgs(Null(String()))            .expect(CHBoolean.TRUE)
                .build();
    }
}
