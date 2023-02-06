package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.d;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dt;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intDay;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intHour;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intMin;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intMonth;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intSec;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intWeek;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intYear;
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
public class PlusLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        return new CasesBuilder(CHFunctions.plus)
                .forArgs(   un8(1),     un8(1))       .expect(un16(2))
                .forArgs(   un16(1),    un16(1))      .expect(un32(2))
                .forArgs(   un32(1),    un32(1))      .expect(un64(2))
                .forArgs(   un64(1),    un64(1))      .expect(un64(2))
                .forArgs(   n8(1),      n8(1))        .expect(n16(2))
                .forArgs(   n16(1),     n16(1))       .expect(n32(2))
                .forArgs(   n32(1),     n32(1))       .expect(n64(2))
                .forArgs(   n64(1),     n64(1))       .expect(n64(2))

                .forArgs(   d("2020-01-01"),            un8(1))      .expect(d("2020-01-02"))
                .forArgs(   dt("2020-01-01 00:00:00"),  un8(1))      .expect(dt("2020-01-01 00:00:01"))

                .forArgs(   d("2020-01-01"),            intSec(1))   .expect(dt("2020-01-01 00:00:01"))
                .forArgs(   d("2020-01-01"),            intMin(1))   .expect(dt("2020-01-01 00:01:00"))
                .forArgs(   d("2020-01-01"),            intHour(1))  .expect(dt("2020-01-01 01:00:00"))
                .forArgs(   d("2020-01-01"),            intDay(1))   .expect(d("2020-01-02"))
                .forArgs(   d("2020-01-01"),            intWeek(1))  .expect(d("2020-01-08"))
                .forArgs(   d("2020-01-01"),            intMonth(1)) .expect(d("2020-02-01"))
                .forArgs(   d("2020-01-01"),            intYear(1))  .expect(d("2021-01-01"))

                .forArgs(   dt("2020-01-01 00:00:00"),  intSec(1))   .expect(dt("2020-01-01 00:00:01"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intMin(1))   .expect(dt("2020-01-01 00:01:00"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intHour(1))  .expect(dt("2020-01-01 01:00:00"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intDay(1))   .expect(dt("2020-01-02 00:00:00"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intWeek(1))  .expect(dt("2020-01-08 00:00:00"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intMonth(1)) .expect(dt("2020-02-01 00:00:00"))
                .forArgs(   dt("2020-01-01 00:00:00"),  intYear(1))  .expect(dt("2021-01-01 00:00:00"))

                .build();
    }
}
