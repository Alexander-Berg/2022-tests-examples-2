package ru.yandex.metrika.segments.core.query;

import java.util.List;
import java.util.Optional;
import java.util.Set;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.literals.CHDate;
import ru.yandex.metrika.segments.clickhouse.types.TArray;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TUInt64;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;
import ru.yandex.metrika.segments.core.parser.AbstractTest;
import ru.yandex.metrika.segments.core.parser.filter.FBFilter;
import ru.yandex.metrika.segments.core.parser.filter.FilterParserBraces2;
import ru.yandex.metrika.segments.core.query.filter.Filter;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Equals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.and;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayArrayFilter;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayFilter;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayMap;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.cond;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.equalsNum;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.greater;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ifNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lambda;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.reshape1to2;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateOrNull;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.core.NullabilityUtils.asNullable;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_BannerID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_Load;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_BannerID;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.FakeTuple_String;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.TrafficSourceID;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_PUID_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.FAKE_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.VISITS;

public class ArrayFilterBuilderTest extends AbstractTest {
    @Test
    public void testTupleFilter() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, false);

        Name<TUInt64> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = arrayFilter(lambda(t, x_0, condition), Adfox_BannerID, Adfox_Load);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testTupleMarks() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, Set.of());

        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = Pair.of(arrayMap(lambda(x_0, condition), Adfox_Load), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testRootFilter() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:trafficSourceID==10");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, false);

        Name<TUInt64> t = n("t");
        Condition condition = cond(equalsNum(TrafficSourceID, n8(10)));
        var expected = arrayFilter(lambda(t, condition), Adfox_BannerID);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testRootMarks() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:trafficSourceID==10");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, Set.of());

        Name<TUInt64> t = n("t");
        Condition condition = cond(equalsNum(TrafficSourceID, n8(10)));
        var expected = Pair.of(arrayMap(lambda(t, condition), Adfox_BannerID), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testMixedFilter() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0 and ym:s:trafficSourceID==10");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, false);

        Name<TUInt64> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(and(greater(x_0, un8(0)), equalsNum(TrafficSourceID, n8(10))));
        var expected = arrayFilter(lambda(t, x_0, condition), Adfox_BannerID, Adfox_Load);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testMixedMarks() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0 and ym:s:trafficSourceID==10");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, Set.of());

        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(and(greater(x_0, un8(0)), equalsNum(TrafficSourceID, n8(10))));
        var expected = Pair.of(arrayMap(lambda(x_0, condition), Adfox_Load), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testMixedFilterWithRetain() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0 and ym:s:trafficSourceID==10");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, true);

        Name<TUInt64> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = arrayFilter(lambda(t, x_0, condition), Adfox_BannerID, Adfox_Load);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testMixedMarksWithRetain() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxLoad>0 and ym:s:trafficSourceID==10");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_TUPLE, Adfox_BannerID, Optional.of(filter), queryContext, 1, Set.of(ADFOX_TUPLE));

        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = Pair.of(arrayMap(lambda(x_0, condition), Adfox_Load), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testDepth2TupleFilter() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, false);

        Name<TUInt64> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = arrayArrayFilter(lambda(t, x_0, condition), Adfox_PuidKey, Adfox_PuidKey);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testDepth2TupleMarks() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, Set.of());

        Name<TArray<TUInt8>> ae_0 = n("_ae_0");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(greater(x_0, un8(0)));
        var expected = Pair.of(arrayMap(lambda(ae_0, arrayMap(lambda(x_0, condition), ae_0)), Adfox_PuidKey), 2);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testDepth2MixedFilter1() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0 and ym:s:trafficSourceID==10");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, false);

        Name<TUInt64> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(and(greater(x_0, un8(0)), equalsNum(TrafficSourceID, n8(10))));
        var expected = arrayArrayFilter(lambda(t, x_0, condition), Adfox_PuidKey, Adfox_PuidKey);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testDepth2MixedMarks1() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0 and ym:s:trafficSourceID==10");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, Set.of());

        Name<TArray<TUInt8>> ae_0 = n("_ae_0");
        Name<TUInt8> x_0 = n("x_0");
        Condition condition = cond(and(greater(x_0, un8(0)), equalsNum(TrafficSourceID, n8(10))));
        var expected = Pair.of(arrayMap(lambda(ae_0, arrayMap(lambda(x_0, condition), ae_0)), Adfox_PuidKey), 2);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testDepth2MixedFilter2() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0 and ym:s:adfoxBannerID!=17");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, false);

        Name<TUInt8> t = n("t");
        Name<TUInt8> x_0 = n("x_0");
        Name<TUInt64> x_1 = n("x_1");
        Condition condition = cond(and(greater(x_0, un8(0)), notEquals(x_1, un64(17))));
        var expected = arrayArrayFilter(lambda(t, x_0, x_1, condition), List.of(Adfox_PuidKey, Adfox_PuidKey, reshape1to2(Adfox_BannerID, Adfox_PuidKey)));

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testDepth2MixedMarks2() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_PUID_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxPuidKey>0 and ym:s:adfoxBannerID!=17");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, Set.of());

        Name<TArray<TUInt8>> ae_0 = n("_ae_0");
        Name<TArray<TUInt64>> ae_1 = n("_ae_1");
        Name<TUInt8> x_0 = n("x_0");
        Name<TUInt64> x_1 = n("x_1");
        Condition condition = cond(and(greater(x_0, un8(0)), notEquals(x_1, un64(17))));
        var expected = Pair.of(arrayMap(lambda(ae_0, ae_1, arrayMap(lambda(x_0, x_1, condition), ae_0, ae_1)), Adfox_PuidKey, reshape1to2(Adfox_BannerID, Adfox_PuidKey)), 2);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testFilterWithSmartLambdanizeWithScalarContext() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxBannerID!=17");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_PUID_TUPLE, Adfox_alias_PuidKey, Optional.of(filter), queryContext, 1, ADFOX_PUID_TUPLE.branchToRoot());

        Name<TUInt8> t = n("t");
        var condition = cond(notEquals(Adfox_alias_BannerID, un64(17)));
        var expected = arrayFilter(lambda(t, condition), Adfox_alias_PuidKey);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testMarksWithSmartLambdanizeWithScalarContext() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(ADFOX_TUPLE).build();

        Filter filter = renderFilter(queryContext, "ym:s:adfoxBannerID!=17");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_PUID_TUPLE, Adfox_alias_PuidKey, Optional.of(filter), queryContext, 1, ADFOX_PUID_TUPLE.branchToRoot());

        Name<TUInt8> t = n("t");
        var condition = cond(notEquals(Adfox_alias_BannerID, un64(17)));
        var expected = Pair.of(arrayMap(lambda(t, condition), Adfox_alias_PuidKey), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testFilterWithSmartLambdanizeWithVectorContext() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).build();

        Filter filter = renderFilter(QueryContext.newBuilder(queryContext).targetTuple(ADFOX_TUPLE).build(), "ym:s:adfoxBannerID!=17");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, ADFOX_PUID_TUPLE.branchToRoot());

        Name<TUInt8> t = n("t");
        Name<TUInt64> x_0 = n("x_0");
        var condition = cond(notEquals(x_0, un64(17)));
        var expected = arrayFilter(lambda(t, x_0, condition), Adfox_PuidKey, Adfox_BannerID);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testMarksWithSmartLambdanizeWithVectorContext() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).build();

        Filter filter = renderFilter(QueryContext.newBuilder(queryContext).targetTuple(ADFOX_TUPLE).build(), "ym:s:adfoxBannerID!=17");
        var marks = ArrayFilterBuilder.buildMarksArraySql(ADFOX_PUID_TUPLE, Adfox_PuidKey, Optional.of(filter), queryContext, 2, ADFOX_PUID_TUPLE.branchToRoot());

        Name<TUInt64> x_0 = n("x_0");
        var condition = cond(notEquals(x_0, un64(17)));
        var expected = Pair.of(arrayMap(lambda(x_0, condition), Adfox_BannerID), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    @Test
    public void testNullableAttributeFilter() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(FAKE_TUPLE).build();

        var filter = renderFilter(queryContext, "ym:s:nullableAttributeWithTuple == '2020-01-01'");
        var arrayFilter = ArrayFilterBuilder.buildFilteredArraySql(FAKE_TUPLE, FakeTuple_String, Optional.of(filter), queryContext, 1, false);

        Name<TString> t = n("t");
        Name<TString> x_0 = n("x_0");
        var condition = cond(Equals(
                toDateOrNull(x_0),
                asNullable(new CHDate(CHDate.dtf.parseLocalDate("2020-01-01")))
        ));
        var expected = arrayFilter(lambda(t, x_0, ifNull(asNullable(condition), b(false))), FakeTuple_String, FakeTuple_String);

        assertEqualExpressions(expected, arrayFilter);
    }

    @Test
    public void testNullableAttributeMarks() {
        QueryContext queryContext = contextBuilder().targetTable(VISITS).targetTuple(FAKE_TUPLE).build();

        var filter = renderFilter(queryContext, "ym:s:nullableAttributeWithTuple == '2020-01-01'");
        var marks = ArrayFilterBuilder.buildMarksArraySql(FAKE_TUPLE, FakeTuple_String, Optional.of(filter), queryContext, 1, Set.of());

        Name<TString> x_0 = n("x_0");
        var condition = cond(Equals(
                toDateOrNull(x_0),
                asNullable(new CHDate(CHDate.dtf.parseLocalDate("2020-01-01")))
        ));
        var expected = Pair.of(arrayMap(lambda(x_0, ifNull(asNullable(condition), b(false))), FakeTuple_String), 1);

        assertEqualExpressions(expected.getLeft(), marks.getLeft());
        assertEquals(expected.getRight(), marks.getRight());
    }

    private Filter renderFilter(QueryContext queryContext, String str) {
        FBFilter fbFilter = new FilterParserBraces2(spp).buildSimpleAST(str, queryContext.getTargetTable());
        return FilterParserBraces2.generateFilter(queryContext, fbFilter, str);
    }
}
