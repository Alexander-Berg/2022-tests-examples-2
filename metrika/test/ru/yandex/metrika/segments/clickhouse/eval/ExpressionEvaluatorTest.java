package ru.yandex.metrika.segments.clickhouse.eval;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.CastExpression;
import ru.yandex.metrika.segments.clickhouse.ast.FunctionCall;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.ast.SQL;
import ru.yandex.metrika.segments.clickhouse.ast.SelectQueryImpl;
import ru.yandex.metrika.segments.clickhouse.ast.Subquery;
import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.clickhouse.eval.compile.ExpressionEvaluator;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.CastException;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.NoMatchingFunctionSignatureFoundException;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.UnevaluatableExpressionException;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.UnresolvableFieldException;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.UnresolvableNameException;
import ru.yandex.metrika.segments.clickhouse.eval.exceptions.UnsupportedFunctionException;
import ru.yandex.metrika.segments.clickhouse.func.CHFunction;
import ru.yandex.metrika.segments.clickhouse.types.CHType;
import ru.yandex.metrika.segments.clickhouse.types.TUInt16;
import ru.yandex.metrika.segments.clickhouse.types.TUInt64;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Date;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.If;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UUID;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.d;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.p;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.plus;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.t2;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.CounterID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Duration;

public class ExpressionEvaluatorTest {

    private MapAliasResolver aliasResolver;
    private MapFieldValueProvider fieldValueProvider;
    private ExpressionEvaluator evaluator;

    @Before
    public void setUp() throws Exception {
        aliasResolver = new MapAliasResolver();
        fieldValueProvider = new MapFieldValueProvider();
        evaluator = new ExpressionEvaluator(aliasResolver, fieldValueProvider);
    }

    @Test
    public void literalUn8Eval() {
        var eval = evaluator.eval(un8(0));
        assertEquals(un8(0), eval);
    }

    @Test
    public void literalStrEval() {
        var eval = evaluator.eval(s("eval"));
        assertEquals(s("eval"), eval);
    }

    @Test
    public void ifEval() {
        var eval = evaluator.eval(If(plus(un8(1), un32(2)).eq(un8(3)), s("makes sense"), s("nonsense")));
        assertEquals(s("makes sense"), eval);
    }

    @Test
    public void castEval() {
        var eval = evaluator.eval(new CastExpression<>(s("2020-01-01"), Date()));
        assertEquals(d("2020-01-01"), eval);
    }

    @Test
    public void fieldEval() {
        fieldValueProvider.putFieldValue(CounterID, un32(10));
        var eval = evaluator.eval(CounterID);
        assertEquals(un32(10), eval);
    }

    @Test
    public void expressionWithFieldEval() {
        fieldValueProvider.putFieldValue(CounterID, un32(10));
        var eval = evaluator.eval(If(CounterID.eq(un32(10)), s("makes sense"), s("nonsense")));
        assertEquals(s("makes sense"), eval);
    }

    @Test
    public void aliasEval() {
        Name<TUInt16> onePlusTwo = n("one_plus_two");
        aliasResolver.register(onePlusTwo, plus(un8(1), un8(2)).toUInt16());
        var eval = evaluator.eval(onePlusTwo);
        assertEquals(un16(3), eval);
    }

    @Test
    public void expressionWithAliasEval() {
        Name<TUInt16> onePlusTwo = n("one_plus_two");
        aliasResolver.register(onePlusTwo, plus(un8(1), un8(2)).toUInt16());
        var eval = evaluator.eval(If(onePlusTwo.eq(un16(3)), s("makes sense"), s("nonsense")));
        assertEquals(s("makes sense"), eval);
    }

    @Test
    public void expressionWithAliasAndFieldEval() {
        Name<TUInt64> durationPlusTen = n("duration_plus_ten");
        aliasResolver.register(durationPlusTen, plus(Duration, un8(10)).toUInt64());
        fieldValueProvider.putFieldValue(Duration, un32(20));

        var eval = evaluator.eval(If(durationPlusTen.eq(un64(30)), s("makes sense"), s("nonsense")));
        assertEquals(s("makes sense"), eval);
    }

    @Test(expected = UnresolvableFieldException.class)
    public void evalUnknownField() {
        evaluator.eval(CounterID);
    }

    @Test(expected = UnresolvableNameException.class)
    public void evalUnknownName() {
        evaluator.eval(n("unknown"));
    }

    @Test(expected = UnevaluatableExpressionException.class)
    public void evalSQLExpression() {
        evaluator.eval(new SQL<>("1=1"));
    }

    @Test(expected = UnevaluatableExpressionException.class)
    public void evalSubquery() {
        evaluator.eval(new Subquery<>(new SelectQueryImpl().select(un8(1)).from(new Table("system.one")).build()));
    }

    @Test(expected = UnevaluatableExpressionException.class)
    public void evalParam() {
        evaluator.eval(p("param"));
    }

    @Test(expected = CastException.class)
    public void evalBadCast() {
        evaluator.eval(new CastExpression<CHType>(t2(un8(0), s("")), UUID()));
    }

    @Test(expected = UnsupportedFunctionException.class)
    public void evalUnknownFunction() {
        var unknownFunction = new CHFunction("unknown_function", false);
        evaluator.eval(new FunctionCall<>(unknownFunction, un8(1)));
    }

    @Test(expected = NoMatchingFunctionSignatureFoundException.class)
    public void evalNotImplementedFunction() {
        var notImplementedFunction = new CHFunction("not_implemented_function", false, new LiteralFunction());
        evaluator.eval(new FunctionCall<>(notImplementedFunction, un8(1)));
    }
}
