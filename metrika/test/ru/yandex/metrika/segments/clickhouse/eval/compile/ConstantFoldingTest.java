package ru.yandex.metrika.segments.clickhouse.eval.compile;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.eval.MapAliasResolver;
import ru.yandex.metrika.segments.clickhouse.literals.CHBoolean;
import ru.yandex.metrika.segments.clickhouse.types.TString;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.If;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.concat;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.divide;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.less;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.plus;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.substring;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Age;

public class ConstantFoldingTest {

    private MapAliasResolver aliasResolver;
    private ExpressionCompiler compiler;

    @Before
    public void setUp() throws Exception {
        aliasResolver = new MapAliasResolver();
        compiler = new ExpressionCompiler(aliasResolver);
    }

    @Test
    public void literalFold() {
        var folded = compiler.constantsFold(un8(0));
        assertEquals(un8(0), folded);
    }

    @Test
    public void simpleFold() {
        var folded = compiler.constantsFold(un8(0).lt(un8(1)));
        assertEquals(CHBoolean.TRUE, folded);
    }

    @Test
    public void complexFold() {
        var folded = compiler.constantsFold(
                If(
                        less(divide(un8(40), un8(3)).toUInt8(), multiply(plus(un8(1), un8(2)), un8(5))),
                        concat(s("constant "), s("folding "), s("works")),
                        concat(s("wrong door, "), s("fellow"))
                )
        );
        assertEquals(s("constant folding works"), folded);
    }

    @Test
    public void partialFold() {
        var folded = compiler.constantsFold(
                If(
                        less(Age, multiply(plus(un8(1), un8(2)), un8(5)).toUInt8()),
                        concat(s("constant "), s("folding "), s("works")),
                        concat(s("wrong door, "), s("fellow"))
                )
        );
        assertEquals(
                If(
                        less(Age, un8(15)),
                        s("constant folding works"),
                        s("wrong door, fellow")
                ),
                folded
        );
    }

    @Test
    public void expressionWithAliasFold() {
        Name<TString> reference = n("reference");
        aliasResolver.register(reference, concat(s("refer"), s("ence")));
        var folded = compiler.constantsFold(reference.eq(substring(s("long reference"), 6, 9)));
        assertEquals(CHBoolean.TRUE, folded);
    }
}
