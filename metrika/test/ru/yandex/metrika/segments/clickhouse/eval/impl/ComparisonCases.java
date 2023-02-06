package ru.yandex.metrika.segments.clickhouse.eval.impl;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.eval.impl.ParametrizedLiteralFunctionTest.CasesBuilder;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.d;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dt;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;

public class ComparisonCases {

    static CasesBuilder lessCases(CasesBuilder casesBuilder, CHLiteral<?> expect) {
        return casesBuilder
                .forArgs(un8(1),                        un8(2))                     .expect(expect)
                .forArgs(un16(1),                       un16(2))                    .expect(expect)
                .forArgs(un32(1),                       un32(2))                    .expect(expect)
                .forArgs(un64(1),                       un64(2))                    .expect(expect)
                .forArgs(n8(1),                         n8(2))                      .expect(expect)
                .forArgs(n16(1),                        n16(2))                     .expect(expect)
                .forArgs(n32(1),                        n32(2))                     .expect(expect)
                .forArgs(n64(1),                        n64(2))                     .expect(expect)
                .forArgs(f32(1.),                       f32(1.1))                   .expect(expect)
                .forArgs(f(1.),                         f(1.1))                     .expect(expect)
                .forArgs(s("a"),                        s("b"))                     .expect(expect)
                .forArgs(d("2020-01-01"),               d("2020-01-02"))            .expect(expect)
                .forArgs(dt("2020-01-01 00:00:00"),     dt("2020-01-01 00:00:01"))  .expect(expect)

                // signed int numbers sanity check
                .forArgs(Int8().minLiteral(),   Int8().maxLiteral())    .expect(expect)
                .forArgs(Int16().minLiteral(),  Int16().maxLiteral())   .expect(expect)
                .forArgs(Int32().minLiteral(),  Int32().maxLiteral())   .expect(expect)
                .forArgs(Int64().minLiteral(),  Int64().maxLiteral())   .expect(expect)

                // unsigned int numbers sanity check
                // also checks that comparison is unsigned for unsigned int numbers
                .forArgs(UInt8().minLiteral(),  UInt8().maxLiteral())   .expect(expect)
                .forArgs(UInt16().minLiteral(), UInt16().maxLiteral())  .expect(expect)
                .forArgs(UInt32().minLiteral(), UInt32().maxLiteral())  .expect(expect)
                .forArgs(UInt64().minLiteral(), UInt64().maxLiteral())  .expect(expect);
    }

    static CasesBuilder greaterCases(CasesBuilder casesBuilder, CHLiteral<?> expect) {
        return casesBuilder
                .forArgs(un8(1),                        un8(0))                     .expect(expect)
                .forArgs(un16(1),                       un16(0))                    .expect(expect)
                .forArgs(un32(1),                       un32(0))                    .expect(expect)
                .forArgs(un64(1),                       un64(0))                    .expect(expect)
                .forArgs(n8(1),                         n8(0))                      .expect(expect)
                .forArgs(n16(1),                        n16(0))                     .expect(expect)
                .forArgs(n32(1),                        n32(0))                     .expect(expect)
                .forArgs(n64(1),                        n64(0))                     .expect(expect)
                .forArgs(f32(1.),                       f32(0.1))                   .expect(expect)
                .forArgs(f(1.),                         f(0.1))                     .expect(expect)
                .forArgs(s("b"),                        s("a"))                     .expect(expect)
                .forArgs(d("2020-01-02"),               d("2020-01-01"))            .expect(expect)
                .forArgs(dt("2020-01-01 00:00:01"),     dt("2020-01-01 00:00:00"))  .expect(expect)

                // signed int numbers sanity check
                .forArgs(Int8().maxLiteral(),   Int8().minLiteral())    .expect(expect)
                .forArgs(Int16().maxLiteral(),  Int16().minLiteral())   .expect(expect)
                .forArgs(Int32().maxLiteral(),  Int32().minLiteral())   .expect(expect)
                .forArgs(Int64().maxLiteral(),  Int64().minLiteral())   .expect(expect)

                // unsigned int numbers sanity check
                // also checks that comparison is unsigned for unsigned int numbers
                .forArgs(UInt8().maxLiteral(),  UInt8().minLiteral())   .expect(expect)
                .forArgs(UInt16().maxLiteral(), UInt16().minLiteral())  .expect(expect)
                .forArgs(UInt32().maxLiteral(), UInt32().minLiteral())  .expect(expect)
                .forArgs(UInt64().maxLiteral(), UInt64().minLiteral())  .expect(expect);
    }

    static CasesBuilder equalsCases(CasesBuilder casesBuilder, CHLiteral<?> expect) {
        return casesBuilder
                .forArgs(un8(1),                        un8(1))                     .expect(expect)
                .forArgs(un16(1),                       un16(1))                    .expect(expect)
                .forArgs(un32(1),                       un32(1))                    .expect(expect)
                .forArgs(un64(1),                       un64(1))                    .expect(expect)
                .forArgs(n8(1),                         n8(1))                      .expect(expect)
                .forArgs(n16(1),                        n16(1))                     .expect(expect)
                .forArgs(n32(1),                        n32(1))                     .expect(expect)
                .forArgs(n64(1),                        n64(1))                     .expect(expect)
                .forArgs(f32(1.),                       f32(1.))                    .expect(expect)
                .forArgs(f(1.),                         f(1.))                      .expect(expect)
                .forArgs(s("a"),                        s("a"))                     .expect(expect)
                .forArgs(d("2020-01-01"),               d("2020-01-01"))            .expect(expect)
                .forArgs(dt("2020-01-01 00:00:00"),     dt("2020-01-01 00:00:00"))  .expect(expect);
    }
}
