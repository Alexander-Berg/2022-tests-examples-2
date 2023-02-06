package ru.yandex.metrika.segments.clickhouse.optim;

import java.util.List;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.ArrayJoin;
import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.SelectQuery;
import ru.yandex.metrika.segments.clickhouse.types.TInt32;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayEnumerateUniqRanked;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayExists;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayFilter;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lambda;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.name;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.select;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.sumIf;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDate;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.uniqIf;
import static ru.yandex.metrika.segments.site.bundles.AttributionUtils.attributed;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.AdfPu_alias_PuidKey;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.AdfPu_alias_PuidVal;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_Load;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_PuidKey;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_PuidVal;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_alias_Load;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_alias_PuidKey;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Adfox_alias_PuidVal;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Age;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.CounterID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Sex;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Sign;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.StartDate;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_Model;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.UserID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.YAN_PageID;
import static ru.yandex.metrika.segments.site.schema.MtLog.visits;

/**
 * Скорее не тест а proof of concept
 */
public class MultiArrayJoinRewriterTest {

    private static final SelectQuery originalQuery =
            select(
                    AdfPu_alias_PuidKey,
                    AdfPu_alias_PuidVal,
                    n("Loads"),
                    n("Visits"),
                    n("Users")
            ).from(
                    select(
                            AdfPu_alias_PuidKey,
                            AdfPu_alias_PuidVal,
                            sumIf(multiply(Sign, Adfox_alias_Load), name("uniq_AdfoxPuid_Level1", UInt8()).eq(un8(1))).as("Loads"),
                            sumIf(Sign, name("uniq_AdfoxPuid_Level0", UInt8()).eq(un8(1))).as("Visits"),
                            uniqIf(UserID, name("uniq_AdfoxPuid_Level0", UInt8()).eq(un8(1))).as("Users")
                    ).from(
                            visits
                    ).arrayJoins(
                            List.of(
                                    ArrayJoin.builder()
                                            .withExpression(Adfox_Load.as(Adfox_alias_Load.getName()))
                                            .withExpression(Adfox_PuidKey.as(Adfox_alias_PuidKey.getName()))
                                            .withExpression(Adfox_PuidVal.as(Adfox_alias_PuidVal.getName()))
                                            .withExpression(arrayEnumerateUniqRanked(List.of(un8(1), Adfox_PuidKey, un8(2), Adfox_PuidVal, un8(2))).as("uniq_AdfoxPuid_Level0_Arr"))
                                            .withExpression(arrayEnumerateUniqRanked(List.of(un8(2), Adfox_PuidKey, un8(2), Adfox_PuidVal, un8(2))).as("uniq_AdfoxPuid_Level1_Arr"))
                                            .build(),
                                    ArrayJoin.builder()
                                            .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), Adfox_alias_PuidKey, Adfox_alias_PuidKey).as(AdfPu_alias_PuidKey.getName()))
                                            .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), Adfox_alias_PuidVal, Adfox_alias_PuidKey).as(AdfPu_alias_PuidVal.getName()))
                                            .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), n("uniq_AdfoxPuid_Level0_Arr"), Adfox_alias_PuidKey).as("uniq_AdfoxPuid_Level0"))
                                            .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), n("uniq_AdfoxPuid_Level1_Arr"), Adfox_alias_PuidKey).as("uniq_AdfoxPuid_Level1"))
                                            .build()
                            )
                    ).where(Condition.and(List.of(
                            attributed(TrafficSource_ID, LAST).ge(n8(1)),
                            AdfPu_alias_PuidKey.ne(un8(0)),
                            CounterID.eq(un32(1)),
                            StartDate.le(toDate("2019-01-01")),
                            StartDate.le(toDate("2018-01-01")),
                            Adfox_alias_Load.gt(un8(0)),
                            Condition.or(Age.ge(un8(30)), Sex.le(un8(15))),
                            new Condition(arrayExists(lambda(n("x"), ClickHouse.<TInt32>n("x").ge(n32(10)).and(AdfPu_alias_PuidKey.le(un8(100)))), YAN_PageID))
                    ))).groupby(
                            AdfPu_alias_PuidKey, AdfPu_alias_PuidVal
                    ).orderBy(
                            AdfPu_alias_PuidKey.asc(), AdfPu_alias_PuidVal.asc()
                    )
            ).build();

    private static final SelectQuery expectedResult =
            select(
                    AdfPu_alias_PuidKey,
                    AdfPu_alias_PuidVal,
                    n("Loads"),
                    n("Visits"),
                    n("Users")
            ).from(
                    select(
                            AdfPu_alias_PuidKey,
                            AdfPu_alias_PuidVal,
                            sumIf(multiply(Sign, Adfox_alias_Load), name("uniq_AdfoxPuid_Level1", UInt8()).eq(un8(1))).as("Loads"),
                            sumIf(Sign, name("uniq_AdfoxPuid_Level0", UInt8()).eq(un8(1))).as("Visits"),
                            uniqIf(UserID, name("uniq_AdfoxPuid_Level0", UInt8()).eq(un8(1))).as("Users")
                    ).from(
                            select(
                                    Age,
                                    CounterID,
                                    Sex,
                                    Sign,
                                    StartDate,
                                    UserID,
                                    Adfox_alias_Load,
                                    Adfox_alias_PuidKey,
                                    Adfox_alias_PuidVal,
                                    TrafficSource_ID, TrafficSource_Model,
                                    YAN_PageID,
                                    n("uniq_AdfoxPuid_Level0_Arr"),
                                    n("uniq_AdfoxPuid_Level1_Arr")
                            ).from(
                                    visits
                            ).arrayJoin(
                                    ArrayJoin.builder()
                                            .withExpression(Adfox_Load.as(Adfox_alias_Load.getName()))
                                            .withExpression(Adfox_PuidKey.as(Adfox_alias_PuidKey.getName()))
                                            .withExpression(Adfox_PuidVal.as(Adfox_alias_PuidVal.getName()))
                                            .withExpression(arrayEnumerateUniqRanked(List.of(un8(1), Adfox_PuidKey, un8(2), Adfox_PuidVal, un8(2))).as("uniq_AdfoxPuid_Level0_Arr"))
                                            .withExpression(arrayEnumerateUniqRanked(List.of(un8(2), Adfox_PuidKey, un8(2), Adfox_PuidVal, un8(2))).as("uniq_AdfoxPuid_Level1_Arr"))
                                            .build()
                            ).where(Condition.and(List.of(
                                    attributed(TrafficSource_ID, LAST).ge(n8(1)),
                                    CounterID.eq(un32(1)),
                                    StartDate.le(toDate("2019-01-01")),
                                    StartDate.le(toDate("2018-01-01")),
                                    Adfox_alias_Load.gt(un8(0)),
                                    Condition.or(Age.ge(un8(30)), Sex.le(un8(15)))
                            )))
                    ).arrayJoin(
                            ArrayJoin.builder()
                                    .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), Adfox_alias_PuidKey, Adfox_alias_PuidKey).as(AdfPu_alias_PuidKey.getName()))
                                    .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), Adfox_alias_PuidVal, Adfox_alias_PuidKey).as(AdfPu_alias_PuidVal.getName()))
                                    .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), n("uniq_AdfoxPuid_Level0_Arr"), Adfox_alias_PuidKey).as("uniq_AdfoxPuid_Level0"))
                                    .withExpression(arrayFilter(lambda(n("x"), n("y"), attributed(TrafficSource_ID, LAST).eq(n8(1)).and(ClickHouse.<TUInt8>n("y").ne(un8(0)))), n("uniq_AdfoxPuid_Level1_Arr"), Adfox_alias_PuidKey).as("uniq_AdfoxPuid_Level1"))
                                    .build()

                    ).where(Condition.and(List.of(
                            attributed(TrafficSource_ID, LAST).ge(n8(1)),
                            AdfPu_alias_PuidKey.ne(un8(0)),
                            CounterID.eq(un32(1)),
                            StartDate.le(toDate("2019-01-01")),
                            StartDate.le(toDate("2018-01-01")),
                            Adfox_alias_Load.gt(un8(0)),
                            Condition.or(Age.ge(un8(30)), Sex.le(un8(15))),
                            new Condition(arrayExists(lambda(n("x"), ClickHouse.<TInt32>n("x").ge(n32(10)).and(AdfPu_alias_PuidKey.le(un8(100)))), YAN_PageID))
                    ))).groupby(
                            AdfPu_alias_PuidKey, AdfPu_alias_PuidVal
                    ).orderBy(
                            AdfPu_alias_PuidKey.asc(), AdfPu_alias_PuidVal.asc()
                    )
            ).build();

    @Test
    public void rewrite() {
        SelectQuery rewrite = MultiArrayJoinRewriter.rewrite(originalQuery);
        // System.out.println("rewrite = " + PrintQuery.print(rewrite));
        // System.out.println("expecte = " + PrintQuery.print(expectedResult));
        Assert.assertEquals(rewrite, expectedResult);
    }


}
