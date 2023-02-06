package ru.yandex.metrika.segments.core.parser;

import java.util.List;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;

import ru.yandex.metrika.segments.core.query.parts.FromJoin;
import ru.yandex.metrika.segments.core.schema.TableNotAggregatedJoin;

import static org.hamcrest.Matchers.hasItem;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

public class QueryParserNotAggregatedJoinTest extends AbstractTest {

    @Test
    public void test() {
        var queryParams = builder()
                .counterId(24226447)
                .startDate("2019-01-01")
                .endDate("2019-01-01")
                .metrics("ym:pv:pageViews")
                .dimensions("ym:s:trafficSourceID")
                .filtersBraces2("ym:s:trafficSourceID IN ('1', '2')")
                .limit(10)
                .build();
        var query = apiUtils.parseQuery(queryParams);

        assertTrue(query.getQueryContext().getTargetTable() instanceof TableNotAggregatedJoin);
        var joinTable = (TableNotAggregatedJoin) query.getQueryContext().getTargetTable();
        assertEquals(SimpleTestTableSchema.VISITS, joinTable.getTableForDimensions());
        assertEquals(SimpleTestTableSchema.HITS, joinTable.getTableForMetrics());
        assertEquals(List.of(bundle.eventID), joinTable.getJoinAttrsForDimensions());
        assertEquals(List.of(bundle.hitsEventID), joinTable.getJoinAttrsForMetrics());

        assertTrue(query.getFromTable() instanceof FromJoin);
        var joinFrom = (FromJoin) query.getFromTable();
        assertTrue(joinFrom.getJoinCondition() instanceof FromJoin.OnJoinCondition);
        var onJoinCondition = (FromJoin.OnJoinCondition) joinFrom.getJoinCondition();
        assertThat(onJoinCondition.onClause, hasItem(Pair.of(bundle.eventID, bundle.hitsEventID)));

        // тут еще много что можно проверять

        // debug
        var sql = query.buildSql();
        System.out.println(sql);
    }
}
