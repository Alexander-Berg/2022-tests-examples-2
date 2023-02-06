package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Array;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Float64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayMap;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.f;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lambda;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.plus;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.eval.compile.CompilerUtils.compilePureLambda;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.CHLiteralTestUtils.arr;

public class ArrayMapLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        var x = new Name<>("x", UInt8());
        var y = new Name<>("y", Float64());

        var xArr = new Name<>("xArr", Array(UInt8()));
        var yArr = new Name<>("yArr", Array(Float64()));

        return new CasesBuilder(CHFunctions.arrayMap)

                .forArgs(
                        compilePureLambda(lambda(x, y, plus(y, multiply(x, x)))),
                        arr(un8(1), un8(2), un8(3)),
                        arr(f(0.1), f(0.2), f(0.3))
                ).expect(
                        arr(f(1.1), f(4.2), f(9.3))
                )

                .forArgs(
                        compilePureLambda(lambda(
                                xArr, yArr,
                                arrayMap(
                                        lambda(x, y, plus(y, multiply(x, x))),
                                        xArr,
                                        yArr
                                )
                        )),
                        arr(
                                arr(un8(1), un8(2), un8(3)),
                                arr(un8(4), un8(5), un8(6))
                        ),
                        arr(
                                arr(f(0.1), f(0.2), f(0.3)),
                                arr(f(0.4), f(0.5), f(0.6))
                        )
                ).expect(
                        arr(
                                arr(f(1.1), f(4.2), f(9.3)),
                                arr(f(16.4), f(25.5), f(36.6))
                        )
                )

                .build();
    }
}
