package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Float64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lambda;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.plus;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.compile.CompilerUtils.compilePureLambda;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;

public class ArrayExistsLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        var x = new Name<>("x", UInt8());
        var y = new Name<>("y", Float64());

        return new CasesBuilder(CHFunctions.arrayExists)

                .forArgs(
                        compilePureLambda(lambda(x, y, plus(y, multiply(x, x)).gt(f(4)))),
                        arr(un8(1), un8(2), un8(3)),
                        arr(f(0.1), f(0.2), f(0.3))
                ).expect(
                        b(true)
                )

                .build();
    }

}
