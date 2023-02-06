package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunctions;

import static ru.yandex.metrika.segments.clickhouse.eval.impl.ComparisonCases.equalsCases;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.ComparisonCases.greaterCases;
import static ru.yandex.metrika.segments.clickhouse.eval.impl.ComparisonCases.lessCases;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.FALSE;
import static ru.yandex.metrika.segments.clickhouse.literals.CHBoolean.TRUE;

public class LessOrEqualsLiteralFunctionTest extends ParametrizedLiteralFunctionTest {

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> cases() {
        var casesBuilder = new CasesBuilder(CHFunctions.lessOrEquals);

        equalsCases(casesBuilder, TRUE);
        lessCases(casesBuilder, TRUE);
        greaterCases(casesBuilder, FALSE);

        return casesBuilder.build();
    }
}
