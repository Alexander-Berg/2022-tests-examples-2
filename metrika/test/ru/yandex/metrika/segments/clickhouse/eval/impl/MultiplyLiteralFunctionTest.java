package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

/**
 * Проверок для чисел с плавающей точкой тут нет и не будет, потому что арифметика над ними не позволяет
 * нормально проверять результат на равенство с ожидаемым результатом
 */
public class MultiplyLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.multiply)
                .forArgs(   un8(2),     un8(2))       .expect(un16(4))
                .forArgs(   un16(2),    un16(2))      .expect(un32(4))
                .forArgs(   un32(2),    un32(2))      .expect(un64(4))
                .forArgs(   un64(2),    un64(2))      .expect(un64(4))
                .forArgs(   n8(2),      n8(2))        .expect(n16(4))
                .forArgs(   n16(2),     n16(2))       .expect(n32(4))
                .forArgs(   n32(2),     n32(2))       .expect(n64(4))
                .forArgs(   n64(2),     n64(2))       .expect(n64(4))

                .build();
    }
}
