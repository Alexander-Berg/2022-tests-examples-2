package ru.yandex.metrika.segments.core.query.filter;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.literals.CHDate;
import ru.yandex.metrika.segments.clickhouse.types.TDate;
import ru.yandex.metrika.segments.clickhouse.types.TUInt64;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;
import ru.yandex.metrika.segments.core.parser.AbstractTest;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.parts.Relation;
import ru.yandex.metrika.segments.core.schema.AttributeEntity;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayArrayExists;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayExists;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ifNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lambda;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateOrNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.core.NullabilityUtils.asNullable;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_BannerID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.FakeTuple_String;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_PUID_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.FAKE_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.VISITS;

public class TupleFilterTest extends AbstractTest {

    @Test
    public void testBuildExpressionDepth1() {
        TupleFilter tupleFilter = new TupleFilter(
                Quantifier.EXISTS,
                new AttributeEntity(VISITS, ADFOX_TUPLE),
                new SelectPartFilterValues(bundle.adfoxBannerID, Relation.EQ, "10", false)
        );

        QueryContext context = contextBuilder().targetTable(VISITS).build();
        Condition condition = tupleFilter.buildExpression(context);

        Name<TUInt64> x_0 = n("x_0");
        var expected = arrayExists(lambda(x_0, x_0.eq(un64(10))), Adfox_BannerID);

        assertEqualExpressions(expected, condition);
    }

    @Test
    public void testBuildExpressionDepth2() {
        TupleFilter tupleFilter = new TupleFilter(
                Quantifier.EXISTS,
                new AttributeEntity(VISITS, ADFOX_PUID_TUPLE),
                new SelectPartFilterValues(bundle.adfoxPuidKey, Relation.EQ, "10", false)
        );

        QueryContext context = contextBuilder().targetTable(VISITS).build();
        Condition condition = tupleFilter.buildExpression(context);

        Name<TUInt8> x_0 = n("x_0");
        var expected = arrayArrayExists(lambda(x_0, x_0.eq(un8(10))), List.of(Adfox_PuidKey));

        assertEqualExpressions(expected, condition);
    }

    @Test
    public void testBuildExpressionDepth1WithContextDepth1() {
        TupleFilter tupleFilter = new TupleFilter(
                Quantifier.EXISTS,
                new AttributeEntity(VISITS, ADFOX_PUID_TUPLE),
                new SelectPartFilterValues(bundle.adfoxPuidKey, Relation.EQ, "10", false)
        );

        QueryContext context = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();
        Condition condition = tupleFilter.buildExpression(context);

        Name<TUInt8> x_0 = n("x_0");
        var expected = arrayExists(lambda(x_0, x_0.eq(un8(10))), List.of(Adfox_alias_PuidKey));

        assertEqualExpressions(expected, condition);
    }

    @Test
    public void testBuildExpressionForNullable() {
        var tupleFilter = new TupleFilter(
                Quantifier.EXISTS,
                new AttributeEntity(VISITS, FAKE_TUPLE),
                new SelectPartFilterValues(bundle.nullableAttributeWithTuple, Relation.EQ, "2020-01-01", false)
        );

        var context = contextBuilder().targetTable(VISITS).build();
        var condition = tupleFilter.buildExpression(context);

        Name<TDate> x_0 = n("x_0");
        var expected = arrayExists(lambda(x_0, ifNull(asNullable(toDateOrNull(x_0).eq(asNullable(new CHDate(CHDate.dtf.parseLocalDate("2020-01-01"))))), b(false))), FakeTuple_String);

        assertEqualExpressions(expected, condition);
    }
}
