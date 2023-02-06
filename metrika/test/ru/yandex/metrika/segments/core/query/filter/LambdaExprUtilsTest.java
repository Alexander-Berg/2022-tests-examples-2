package ru.yandex.metrika.segments.core.query.filter;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.schema.TargetTuple;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.Issue;
import ru.yandex.metrika.util.collections.F;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfPu_alias_PuidKey;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.AdfPu_alias_PuidVal;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.Adfox_alias_BannerID;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_PUID_TUPLE;
import static ru.yandex.metrika.segments.core.parser.SimpleTestTableSchema.ADFOX_TUPLE;

/**
 * TODO: добавить больше тестов
 */
@Issue(key = "METR-33587")
public class LambdaExprUtilsTest {

    @Test
    public void testFindColumnsExprRecursive() {
        QueryContext qctx = QueryContext
                .smallContextBuilder(new HashMap<>(), "ru", "ru")
                .startDate("today")
                .endDate("today")
                .targetTable(TableSchemaSite.VISITS)
                .build();

        Condition condition = AdfPu_alias_PuidKey.eq(un8(7)).and(Adfox_alias_BannerID.le(un64(13))).or(AdfPu_alias_PuidVal.eq(un32(11)));
        Map<TargetTuple, List<Expression<?>>> result = LambdaExprUtils.findColumnsScalarExprRecursive(condition, ADFOX_PUID_TUPLE, false, qctx);
        assertEquals(
                Map.of(
                        ADFOX_PUID_TUPLE, Set.of(AdfPu_alias_PuidKey, AdfPu_alias_PuidVal),
                        ADFOX_TUPLE, Set.of(Adfox_alias_BannerID)
                ),
                F.mapValues(result, Set::copyOf)
        );
    }
}
