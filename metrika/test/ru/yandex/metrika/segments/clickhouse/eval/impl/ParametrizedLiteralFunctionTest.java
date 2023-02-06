package ru.yandex.metrika.segments.clickhouse.eval.impl;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.ast.FunctionCall;
import ru.yandex.metrika.segments.clickhouse.eval.compile.ExpressionEvaluator;
import ru.yandex.metrika.segments.clickhouse.func.CHFunction;
import ru.yandex.metrika.segments.clickhouse.literals.CHNull;
import ru.yandex.metrika.segments.clickhouse.parse.PrintQuery;
import ru.yandex.metrika.segments.clickhouse.types.CHType;
import ru.yandex.metrika.util.collections.F;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.isNull;

@RunWith(Parameterized.class)
public abstract class ParametrizedLiteralFunctionTest {
    @Parameterized.Parameter
    public CHFunction function;

    @Parameterized.Parameter(1)
    public List<CHLiteral<?>> args;

    @Parameterized.Parameter(2)
    public CHLiteral<?> expectedResult;

    @Parameterized.Parameter(3)
    public String sql;

    @Test
    public void test() {
        var resultO = function.getLiteralFunction().apply(args);
        if (resultO.isEmpty()) {
            Assert.fail("Cannot apply args " + F.map(args, CHLiteral::asSql) + " (types " + F.map(args, l -> l.getType().getName())  + ") to function \"" + function.getName() + "\"");
        }
        var result = resultO.get();
        Assert.assertEquals(
                "Function " + function.getName() + ", args " + F.map(args, CHLiteral::asSql) + " (types " + F.map(args, l -> l.getType().getName()) + ")",
                expectedResult,
                result
        );
    }

    public static class CasesBuilder {
        private final CHFunction chFunction;
        private final List<CaseBuilder> caseBuilders = new ArrayList<>();

        public CasesBuilder(CHFunction chFunction) {
            this.chFunction = chFunction;
        }

        protected CaseBuilder forArgs(Expression<?>... args) {
            var caseBuilder = new CaseBuilder(this, List.of(args));
            caseBuilders.add(caseBuilder);
            return caseBuilder;
        }

        protected Collection<Object[]> build() {
            return F.map(caseBuilders, CaseBuilder::build);
        }
    }

    protected static class CaseBuilder {

        private final CasesBuilder casesBuilder;

        private final List<Expression<?>> args;
        private Expression<?> expectedResult;


        private CaseBuilder(CasesBuilder casesBuilder, List<Expression<?>> args) {
            this.casesBuilder = casesBuilder;
            this.args = args;
        }

        protected CasesBuilder expect(Expression<?> expectedResult) {
            this.expectedResult = expectedResult;
            return casesBuilder;
        }

        private Object[] build() {
            return new Object[] {
                    casesBuilder.chFunction,
                    F.map(args, ExpressionEvaluator::staticEval),
                    ExpressionEvaluator.staticEval(expectedResult),
                    buildSqlString()
            };
        }

        private String buildSqlString() {
            var functionCall = new FunctionCall<>(casesBuilder.chFunction, args);
            var expression = expectedResult instanceof CHNull ?
                    isNull(functionCall) : functionCall.eq((Expression<CHType>) expectedResult);
            return PrintQuery.print(expression);
        }
    }
}
