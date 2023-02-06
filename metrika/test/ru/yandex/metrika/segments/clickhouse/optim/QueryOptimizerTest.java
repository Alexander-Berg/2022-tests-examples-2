package ru.yandex.metrika.segments.clickhouse.optim;

import java.util.Arrays;

import org.joda.time.LocalDate;
import org.joda.time.LocalDateTime;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.Condition;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.ast.Field;
import ru.yandex.metrika.segments.clickhouse.ast.Format;
import ru.yandex.metrika.segments.clickhouse.ast.SelectQuery;
import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.clickhouse.literals.CHBoolean;
import ru.yandex.metrika.segments.clickhouse.parse.PrintQuery;
import ru.yandex.metrika.segments.clickhouse.types.TBoolean;
import ru.yandex.metrika.segments.clickhouse.types.TDateTime;
import ru.yandex.metrika.segments.clickhouse.types.TFloat64;
import ru.yandex.metrika.segments.clickhouse.types.TInt32;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TUInt64;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;
import ru.yandex.metrika.segments.core.schema.Dictionary;
import ru.yandex.metrika.segments.site.schema.MtLog;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.DateTime;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Equals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Float64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.If;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ToString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.and;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.arrayElement;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.b;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.concat;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.count;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.d;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dictGetString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dictGetStringOrDefault;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.divide;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.dt;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.greater;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.in;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.intDiv;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lessOrEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.like;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.lower;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.max;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.minus64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.name;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.notEquals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.or;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.splitByChar;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.sum;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.sumIf;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDate;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toDateTime;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toInt32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt64OrZero;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.site.bundles.AttributionUtils.attributed;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.FIRST;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Age;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.CookieEnable;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.CounterID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Referer;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.ResolutionHeight;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.ResolutionWidth;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.Sign;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.StartDate;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickClientID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickGroupBannerID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickIsGoodConversion;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickOrderID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickPlaceID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_StartTime;

/**

 * Created by orantius on 13.07.16.
 */
public class QueryOptimizerTest {

    // and(equals(TraficSourceID,2),equals(if(equals(TraficSourceID,2),SEToRoot(toUInt8(SearchEngineID)),0),26))




/*
((multiply(divide(multiply(
sumIf(multiply(1,Sign),

    @Test
and(
    and(
        and(
            greater(if(notEquals(toDate(FirstVisit),toDate('0000-00-00')),
                        if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                            -2,
                            intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                        -2),
                    7),
            and(
                notEquals(toDate(FirstVisit),toDate('0000-00-00')),
                notEquals(if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                            -2,
                            intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                        -2))),
        and(
            notEquals(toDate(FirstVisit),toDate('0000-00-00')),
            notEquals(if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                        -2,
                        intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                    -2))),
    and(
        and(
            lessOrEquals(if(notEquals(toDate(FirstVisit),toDate('0000-00-00')),
                            if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                                -2,
                                intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                            -2),
                        31),
            and(
                notEquals(toDate(FirstVisit),toDate('0000-00-00')),
                notEquals(if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                            -2,
                            intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                        -2))),
        and(
            notEquals(toDate(FirstVisit),toDate('0000-00-00')),
            notEquals(if(lessOrEquals(FirstVisit,toDateTime(toDate('1970-01-02'))),
                        -2,
                        intDiv(minus(toUInt64(StartTime),toUInt64(FirstVisit)),86400)),
                    -2))),
    in(_uniq_ParsedParams,tuple(0,1)))),10),multiply(sumIf(multiply(1,Sign),in(_uniq_ParsedParams,tuple(0,1))),10)),100.0)) AS `ym:s:upToMonthSinceFirstVisitPercentage`)
* */

    @Test
    public void newUsersTest4() {
        Expression<TBoolean> arg =
                and(
                        and(
                                and(
                                        greater(If(notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
        If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                                                n64(-2)),
        n64(7)),
        and(
                notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
                notEquals(If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                        n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                        n64(-2)))),
        and(
                notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
                notEquals(If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                        n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                        n64(-2)))),
        and(
                and(
                        lessOrEquals(If(notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
        If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                                n64(-2)),
        n64(31)),
        and(
                notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
                notEquals(If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                        n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                        n64(-2)))),
        and(
                notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)),d((LocalDate) null)),
                notEquals(If(lessOrEquals(attributed(TrafficSource_StartTime, FIRST),toDateTime(toDate("1970-01-02"))),
                        n64(-2),
                intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)),toUInt64(attributed(TrafficSource_StartTime, FIRST))),n64(86400))),
                        n64(-2)))));

        SelectQuery select = ClickHouse.select(name("a")).where(new Condition(arg)).build();
        Expression<?> ss = QueryOptimizer.simplifyExpressions(select, true, false).getWhere().get();
        System.out.println("ss = " + ss);
    }

    @Test
    public void newUsersTest3() {
        Expression<TBoolean> arg =
        greater(If (notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)), d((LocalDate) null)),
                If (lessOrEquals(attributed(TrafficSource_StartTime, FIRST), toDateTime("1970-01-02 00:00:00")),
                        n64(-2), intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)), toUInt64(attributed(TrafficSource_StartTime, FIRST))), n64(86400))),n64(-2)),n64(7));
        SelectQuery select = ClickHouse.select(name("a")).where(new Condition(arg)).build();
        Expression<?> ss = QueryOptimizer.simplifyExpressions(select, true, false).getWhere().get();
        System.out.println("ss = " + ss);
    }

    @Test
    public void newStrTest() {
        Expression<TBoolean> arg = and(Equals(Referer, s("abc_")), like(Referer, s("abc\\_")));
        SelectQuery select = ClickHouse.select(name("a")).where(new Condition(arg)).build();
        Expression<?> ss = QueryOptimizer.simplifyExpressions(select, true, false).getWhere().get();
        System.out.println("ss = " + ss);
        assertNotEquals(ss, CHBoolean.FALSE);
    }

    @Test
    public void newUsersTest2() {
        Expression<TBoolean> arg =
            and(and(greater( If (notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)), d((LocalDate) null)),
                        If (lessOrEquals(attributed(TrafficSource_StartTime, FIRST), toDateTime(toDate("1970-01-02"))),
                                n64(-2), intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)), toUInt64(attributed(TrafficSource_StartTime, FIRST))), n64(86400))),n64(-2)),n64(7)),
                    and(notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)), d((LocalDate) null)), notEquals(
                    If (lessOrEquals(attributed(TrafficSource_StartTime, FIRST), toDateTime(toDate("1970-01-02"))),
                            n64(-2), intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)), toUInt64(attributed(TrafficSource_StartTime, FIRST))), n64(86400))),n64(-2)))),
                and(notEquals(toDate(attributed(TrafficSource_StartTime, FIRST)), d((LocalDate) null)), notEquals(
                    If (lessOrEquals(attributed(TrafficSource_StartTime, FIRST), toDateTime(toDate("1970-01-02"))),
                        n64(-2), intDiv(minus64(toUInt64(attributed(TrafficSource_StartTime, LAST)), toUInt64(attributed(TrafficSource_StartTime, FIRST))), n64(86400))),n64(-2))));
        SelectQuery select = ClickHouse.select(arg).build();
        Expression<?> ss = QueryOptimizer.simplifyExpressions(select, true, false).getSelect().get(0);
        System.out.println("ss = " + ss);
    }
    public void newUsersTest () {
        Expression<TBoolean> arg =
                and(Equals(and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32),
                        and(Equals(attributed(TrafficSource_ID,LAST),n8(3)),attributed(TrafficSource_ClickIsGoodConversion,LAST))), CHBoolean.TRUE),
                        Equals(If(Equals(and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32),
                                and(Equals(attributed(TrafficSource_ID,LAST),n8(3)),attributed(TrafficSource_ClickIsGoodConversion,LAST))),CHBoolean.TRUE),
                                toUInt8(If(greater(StartDate,toDate("2014-12-03")),
                                        Equals(attributed(TrafficSource_StartTime, FIRST), attributed(TrafficSource_StartTime, LAST)),
                                        Equals(intDiv(toUInt32(attributed(TrafficSource_StartTime, FIRST)),1800),intDiv(toUInt32(attributed(TrafficSource_StartTime, LAST)),1800)))),
                                un8(2)),un8(1)));
        /*and(Equals(and(Equals(PlaceID,n32(542)),and(Equals(TraficSourceID,n8(3)),greater(ClickGoodEvent,n32(0)))),CHBoolean.TRUE),
                Equals(If(Equals(and(Equals(PlaceID,n32(542)),and(Equals(TraficSourceID,n8(3)),greater(ClickGoodEvent,n32(0)))),CHBoolean.TRUE),
                        If(greater(StartDate,toDate("2014-12-03")),
                                Equals(FirstVisit,StartTime),
                                Equals(intDiv(toUInt32(FirstVisit),1800),intDiv(toUInt32(StartTime),1800))),
                        CHBoolean.NULL),CHBoolean.TRUE)).as("isNewUser");*/

        SelectQuery select = ClickHouse.select(arg).build();
        Expression<?> ss = QueryOptimizer.simplifyExpressions(select, true, false).getSelect().get(0);
        System.out.println("ss = " + ss);
    }

   /* @Test
    public void seRootTest2() {

        Expression<TBoolean> arg =
                and(and(greaterOrEquals(StartDate,toDate("2016-05-02")),lessOrEquals(StartDate,toDate("2016-07-03")),Equals(CounterID,un32(1315865))),
                    and(Equals(TraficSourceID,n8(2)),Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(26))));
        SelectQuery select = ClickHouse.select(name("a"))
                .where(new Condition(arg)).build();
        Expression<TBoolean> where = QueryOptimizer.simplifyExpressions(select, true).getWhere().get();
        System.out.println("where = " + where);
    }*/

    /*@Test
    public void seRootTest() {
        Expression<TBoolean> arg =
            and(
                notEquals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(0)),
                or(Arrays.asList(Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(0)),
                        Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(26)),
                        Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(27)),
                        Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(34)),
                        Equals(If(Equals(TraficSourceID,n8(2)),SEToRoot(toUInt8(SearchEngineID)),un8(0)),un8(36)))));

        SelectQuery select = ClickHouse.select(name("a"))
                .where(new Condition(arg)).build();
        Expression<TBoolean> where = QueryOptimizer.simplifyExpressions(select, true).getWhere().get();
        System.out.println("where = " + where);
        System.out.println("where = " + PrintQuery.print(where));
    }*/

    @Test
    public void screenFormatTest() throws Exception {
        Expression<TBoolean> arg =
                Equals(If(greater(ResolutionHeight, un16(0)), If(in(toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16s(9, 11, 12, 13, 14, 15, 16, 26, 28, 31, 33, 35, 37, 49)), toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16(0)), un16(0)), un16(37));

        /*Expression<TBoolean> arg = and(
                Equals(If(greater(ResolutionHeight, un32(0)), If(in(toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16s(9, 11, 12, 13, 14, 15, 16, 26, 28, 31, 33, 35, 37, 49)), toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16(0)), un16(0)), un16(37)),
                notEquals(If(greater(ResolutionHeight, un32(0)), If(in(toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16s(9, 11, 12, 13, 14, 15, 16, 26, 28, 31, 33, 35, 37, 49)), toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16(0)), un16(0)), un16(0)));*/

        SelectQuery select = ClickHouse.select(name("a"))
                .where(new Condition(arg)).build();
        Expression<TBoolean> where = QueryOptimizer.simplifyExpressions(select, true, false).getWhere().get();
        System.out.println("where = " + where);
        System.out.println("where = " + PrintQuery.print(where));
        /* (
        (
        toUInt16(ResolutionWidth * 21 / ResolutionHeight) = 37 OR
        toUInt16(ResolutionWidth * 21 / ResolutionHeight) NOT IN (9,11,12,13,14,15,16,26,28,31,33,35,37,49)
        ) AND ResolutionHeight > 0 OR ResolutionHeight <= 0)


ResolutionHeight >0 and toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)) = 37


        */
    }


    @Test
    public void inTuple() throws Exception {
        SelectQuery select = ClickHouse.select(name("a"))
                .where(CookieEnable.eq(CHBoolean.FALSE).and(Age.eq(un8(16))).or(CookieEnable.eq(CHBoolean.FALSE).and(Age.eq(un8(17))))).build();
        Expression<TBoolean> where = QueryOptimizer.simplifyExpressions(select, true, false).getWhere().get();
        System.out.println("where = " + where);
        System.out.println("where = " + PrintQuery.print(where));
    }

    @Test
    public void andArgumentsWithAlias() throws Exception {
        {
            SelectQuery select = ClickHouse.select(or(and(CookieEnable.eq(CHBoolean.TRUE).as("a"), CookieEnable.eq(CHBoolean.TRUE)), name("a"))).build();
            Expression<?> expression = QueryOptimizer.simplifyExpressions(select, true, false).getSelect().get(0);

            assertEquals(expression, CookieEnable.as("a"));
        }
        {
            SelectQuery select = ClickHouse.select(or(name("a"), and(CookieEnable.eq(CHBoolean.TRUE), CookieEnable.eq(CHBoolean.TRUE).as("a")))).build();
            Expression<?> expression = QueryOptimizer.simplifyExpressions(select, true, false).getSelect().get(0);

            assertEquals(expression, CookieEnable.as("a"));
        }
    }

    @Test
    public void goodEventFilter() throws Exception {
        {
            SelectQuery select = ClickHouse.select(
                    If(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)), attributed(TrafficSource_ClickGroupBannerID,LAST), un64(0)).as("ym:ad:lastDirectBannerGroup"),
                    If(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)), attributed(TrafficSource_ClickOrderID,LAST), un64(0)).as("ym:ad:lastDirectOrder"),
                    max(If(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)), dictGetStringOrDefault(MtLog.campaigns.name,toUInt64(attributed(TrafficSource_ClickOrderID,LAST)), ToString(attributed(TrafficSource_ClickOrderID,LAST))), s("0"))).as("ym:ad:lastDirectOrderName2"),
                    multiply(sumIf(Sign, attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST))), 100).as("ym:ad:visits")
            ).from(MtLog.visits_layer).sample(0.01)
            .where(StartDate.ge(toDate("2015-08-19")).and(StartDate.le(toDate("2016-08-18"))).and(CounterID.eq(un32(1310521))).and(attributed(TrafficSource_ClickClientID,LAST).eq(un32(1288522)))
                        .and(attributed(TrafficSource_ClickGroupBannerID,LAST).eq(un64(929564036)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST))
                            .or(attributed(TrafficSource_ClickGroupBannerID,LAST).eq(un64(710794480)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)))
                            .or(attributed(TrafficSource_ClickGroupBannerID,LAST).eq(un64(303433116)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)))
                            .or(attributed(TrafficSource_ClickGroupBannerID,LAST).eq(un64(619121978)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)))
                            .or(attributed(TrafficSource_ClickGroupBannerID,LAST).eq(un64(352955356)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)))
                        ).and(attributed(TrafficSource_ClickGroupBannerID,LAST).ne(un64(0)).and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ID,LAST).eq(n8(3))).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)))
            ).groupby(Arrays.asList(n("ym:ad:lastDirectBannerGroup"),n("ym:ad:lastDirectOrder")))
            .build();
            SelectQuery selectQuery = QueryOptimizer.simplifyExpressions(select, true, false);

            System.out.println("selectQuery = \n" + PrintQuery.print(selectQuery));
        }
    }

    static class DimFpsStructureDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> macroregion = v("macroregion");
        public final Dictionary.Value<TUInt64, TString> ufps = v("ufps");
        public final Dictionary.Value<TUInt64, TString> post_object = v("post_object");
        public final Dictionary.Value<TUInt64, TString> post_object_no_index = v("post_object_no_index");

        public DimFpsStructureDictionary() {
            super("dim_fps_structure", n("Id"));
        }
    }

    static class PlaceTypeDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> name = v("name");

        public PlaceTypeDictionary() {
            super("place_type", n("Id"));
        }
    }

    static class PayTypeDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> name = v("name");

        public PayTypeDictionary() {
            super("pay_type", n("Id"));
        }
    }

    static class MailTypeDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> name = v("name");

        public MailTypeDictionary() {
            super("mail_type", n("Id"));
        }
    }

    static class MailCtgDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> name = v("name");

        public MailCtgDictionary() {
            super("mailctg", n("Id"));
        }
    }

    static class SenderCtgDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> value = v("value");

        public SenderCtgDictionary() {
            super("sender_ctg", n("Id"));
        }
    }

    static class DirectCtgDictionary extends Dictionary<TUInt64> {
        public final Dictionary.Value<TUInt64, TString> name = v("name");

        public DirectCtgDictionary() {
            super("direct_ctg", n("Id"));
        }
    }

    @Test
    @Ignore("METRIQA-936")
    public void testQuery() throws Exception {
        DimFpsStructureDictionary dim_fps_structure = new DimFpsStructureDictionary();
        PlaceTypeDictionary place_type = new PlaceTypeDictionary();
        PayTypeDictionary payType = new PayTypeDictionary();
        MailTypeDictionary mailtype = new MailTypeDictionary();
        MailCtgDictionary mailctg = new MailCtgDictionary();
        SenderCtgDictionary sender_ctg = new SenderCtgDictionary();
        DirectCtgDictionary direct_ctg = new DirectCtgDictionary();

        Table tg = new Table("tg");
        Table traffic_dist = new Table(tg, "traffic_dist");

        Field<TString> ops_from_code = ClickHouse.field(tg, "ops_from_code", String());
        Field<TString> ops_to_code = ClickHouse.field(tg, "ops_to_code", String());
        Field<TUInt8> ops_from_type_code = ClickHouse.field(tg, "ops_from_type_code", UInt8());
        Field<TUInt8> ops_to_type_code = ClickHouse.field(tg, "ops_to_type_code", UInt8());
        Field<TFloat64> forward_price = ClickHouse.field(tg, "forward_price", Float64());
        Field<TInt32> price = ClickHouse.field(tg, "price", Int32());
        Field<TFloat64> tax_price = ClickHouse.field(tg, "tax_price", Float64());
        Field<TInt32> mass = ClickHouse.field(tg, "mass", Int32());
        Field<TFloat64> index_count = ClickHouse.field(tg, "index_count", Float64());
        Field<TUInt8> pay_type = ClickHouse.field(tg, "pay_type", UInt8());
        Field<TUInt8> mail_type_code = ClickHouse.field(tg, "mail_type_code", UInt8());
        Field<TUInt8> mail_ctg_code = ClickHouse.field(tg, "mail_ctg_code", UInt8());
        Field<TUInt8> send_ctg_code = ClickHouse.field(tg, "send_ctg_code", UInt8());
        Field<TUInt8> direct_ctg_code = ClickHouse.field(tg, "direct_ctg_code", UInt8());
        Field<TDateTime> delivered_oper_date_time = ClickHouse.field(tg, "delivered_oper_date_time", DateTime());
        Field<TDateTime> accepted_oper_date_time = ClickHouse.field(tg, "accepted_oper_date_time", DateTime());
        Field<TDateTime> returned_oper_date_time = ClickHouse.field(tg, "returned_oper_date_time", DateTime());
        Field<TString> inn = ClickHouse.field(tg, "inn", String());
        Field<TString> kpp = ClickHouse.field(tg, "kpp", String());
        Field<TString> bar_code = ClickHouse.field(tg, "bar_code", String());

        SelectQuery query = ClickHouse.select(
                If(toInt8(n8(1)).eq(n8(-1)), s(""), If(toInt8(n8(1)).eq(n8(1)), s(""), If(toInt8(n8(1)).eq(n8(2)), s(""), If(toInt8(n8(1)).eq(n8(3)), s(""), If(toInt8(n8(1)).eq(n8(4)), ops_from_code, s("")))))).as("index_from"),
                If(toInt8(n8(1)).eq(n8(-1)), s(""), If(toInt8(n8(1)).eq(n8(1)), dictGetString(dim_fps_structure.macroregion, toUInt64OrZero(ops_from_code)), If(toInt8(n8(1)).eq(n8(2)), dictGetString(dim_fps_structure.ufps, toUInt64OrZero(ops_from_code)), If(toInt8(n8(1)).eq(n8(3)), dictGetString(dim_fps_structure.post_object_no_index, toUInt64OrZero(ops_from_code)), If(toInt8(n8(1)).eq(n8(4)), ops_from_code, s("")))))).as("from"),
                If(toInt8(n8(-1)).eq(n8(-1)), s(""), dictGetString(place_type.name, toUInt64(ops_from_type_code))).as("type_from"),
                If(toInt8(n8(1)).eq(n8(-1)), s(""), If(toInt8(n8(1)).eq(n8(1)), s(""), If(toInt8(n8(1)).eq(n8(2)), s(""), If(toInt8(n8(1)).eq(n8(3)), s(""), If(toInt8(n8(1)).eq(n8(4)), ops_to_code, s("")))))).as("index_to"),
                If(toInt8(n8(1)).eq(n8(-1)), s(""), If(toInt8(n8(1)).eq(n8(1)), dictGetString(dim_fps_structure.macroregion, toUInt64OrZero(ops_to_code)), If(toInt8(n8(1)).eq(n8(2)), dictGetString(dim_fps_structure.ufps, toUInt64OrZero(ops_to_code)), If(toInt8(n8(1)).eq(n8(3)), dictGetString(dim_fps_structure.post_object_no_index, toUInt64OrZero(ops_to_code)), If(toInt8(n8(1)).eq(n8(4)), ops_to_code, s("")))))).as("to"),
                If(toInt8(n8(-1)).eq(n8(-1)), s(""), dictGetString(place_type.name, toUInt64(ops_to_type_code))).as("type_to"),
                count().as("amount"),
                divide(sum(forward_price), 100).as("send_cost"),
                divide(sum(price), 100).as("cost_size"),
                divide(sum(tax_price), 100).as("cost_rate"),
                divide(sum(mass), 1000).as("sum_weight"),
                sum(index_count).as("number_of_nodes")
        ).from(traffic_dist)
                .where(s("").eq(s("pay_type")).or(s("pay_type").eq(s("pay_type"))).or(concat(s("[Type].["),dictGetString(payType.name,toUInt64(pay_type)),s("]")).eq(s("pay_type")))
                        .and(s("").eq(s("mail_type")).or(s("mail_type").eq(s("mail_type"))).or(concat(s("[Type].["),dictGetString(mailtype.name,toUInt64(mail_type_code)),s("]")).eq(s("mail_type"))))
                        .and(s("").eq(s("mail_ctg")).or(s("mail_ctg").eq(s("mail_ctg"))).or(concat(s("[Category].["),dictGetString(mailctg.name,toUInt64(mail_ctg_code)),s("]")).eq(s("mail_ctg"))))
                        .and(s("").eq(s("ops_from_type")).or(s("ops_from_type").eq(s("ops_from_type"))).or(concat(s("[OPSType].["),dictGetString(place_type.name,toUInt64(ops_from_type_code)),s("]")).eq(s("ops_from_type"))))
                        .and(s("").eq(s("ops_to_type")).or(s("ops_to_type").eq(s("ops_to_type"))).or(concat(s("[OPSType].["),dictGetString(place_type.name,toUInt64(ops_to_type_code)),s("]")).eq(s("ops_to_type"))))
                        .and(s("").eq(s("sender_ctg")).or(s("sender_ctg").eq(s("sender_ctg"))).or(concat(s("[SenderCtg].["),dictGetString(sender_ctg.value,toUInt64(send_ctg_code)),s("]")).eq(s("sender_ctg"))))
                        .and(s("").eq(s("direct_ctg")).or(s("direct_ctg").eq(s("direct_ctg"))).or(concat(s("[DirectCtg].["),dictGetString(direct_ctg.name,toUInt64(direct_ctg_code)),s("]")).eq(s("direct_ctg"))))
                        .and(s("").eq(s("fps_from")).or(s("fps_from").eq(s("fps_from")))
                                .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_from_code)),s("]")).eq(s("fps_from"))
                                        .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_from_code)),s("].["), dictGetString(dim_fps_structure.ufps,toUInt64OrZero(ops_from_code)),s("]")).eq(s("fps_from")))
                                        .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_from_code)),s("].["), dictGetString(dim_fps_structure.ufps,toUInt64OrZero(ops_from_code)),s("].["), dictGetString(dim_fps_structure.post_object,toUInt64OrZero(ops_from_code)),s("]")).eq(s("fps_from")))))
                        .and(s("").eq(s("fps_to")).or(s("fps_to").eq(s("fps_to")))
                                .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_to_code)),s("]")).eq(s("fps_to"))
                                .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_to_code)),s("].["), dictGetString(dim_fps_structure.ufps,toUInt64OrZero(ops_to_code)),s("]")).eq(s("fps_to")))
                                .or(concat(s("[FPS].["),dictGetString(dim_fps_structure.macroregion,toUInt64OrZero(ops_to_code)),s("].["), dictGetString(dim_fps_structure.ufps,toUInt64OrZero(ops_to_code)),s("].["), dictGetString(dim_fps_structure.post_object,toUInt64OrZero(ops_to_code)),s("]")).eq(s("fps_to")))))
                        .and(s("").eq(s("")).or(delivered_oper_date_time.ge(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(delivered_oper_date_time.le(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(accepted_oper_date_time.ge(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(accepted_oper_date_time.le(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(returned_oper_date_time.ge(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(returned_oper_date_time.le(dt((LocalDateTime)null))))
                        .and(s("").eq(s("")).or(like(inn,concat(s("%"),s(""),s("%")))))
                        .and(s("").eq(s("")).or(like(kpp,concat(s("%"),s(""),s("%")))))
                        .and( concat("",s("")).eq(s(""))
                                .or(arrayElement(splitByChar(";", s("")),1).ne(s("")).and(like(lower(bar_code), lower(arrayElement(splitByChar(";", s("")),1))) ) )
                                .or(arrayElement(splitByChar(";", concat("",s(";"))),2).ne(s("")).and(like(lower(bar_code), lower(arrayElement(splitByChar(";", concat("",s(";"))),2))) ) )
                                .or(arrayElement(splitByChar(";", concat("",s(";;"))),3).ne(s("")).and(like(lower(bar_code), lower(arrayElement(splitByChar(";", concat("",s(";;"))),3))) ) )
                                .or(arrayElement(splitByChar(";", concat("",s(";;;"))),4).ne(s("")).and(like(lower(bar_code), lower(arrayElement(splitByChar(";", concat("",s(";;;"))),4))) ) )
                                .or(arrayElement(splitByChar(";", concat("",s(";;;;"))),4).ne(s("")).and(like(lower(bar_code), lower(arrayElement(splitByChar(";", concat("",s(";;;;"))),4))) ) )
                                .or(arrayElement(splitByChar(";", s("")),1).ne(s(""))
                                        .and(arrayElement(splitByChar(";", concat("",s(";"))),2).ne(s("")))
                                        .and(lower(bar_code).ge(lower(arrayElement(splitByChar(";", s("")),1))))
                                        .and(lower(bar_code).le(lower(arrayElement(splitByChar(";", concat("",s(";"))),2)))))
                                .or(arrayElement(splitByChar(";", concat(s(""),";;")),3).ne(s(""))
                                        .and(arrayElement(splitByChar(";", concat("",s(";;;"))),4).ne(s("")))
                                        .and(lower(bar_code).ge(lower(arrayElement(splitByChar(";", concat(s(""),";;")),3))))
                                        .and(lower(bar_code).le(lower(arrayElement(splitByChar(";", concat("",s(";;;"))),4)))))
                                .or(arrayElement(splitByChar(";", concat(s(""),";;;;")),5).ne(s(""))
                                        .and(arrayElement(splitByChar(";", concat("",s(";;;;;"))),6).ne(s("")))
                                        .and(lower(bar_code).ge(lower(arrayElement(splitByChar(";", concat(s(""),";;;;")),5))))
                                        .and(lower(bar_code).le(lower(arrayElement(splitByChar(";", concat("",s(";;;;;"))),6)))))
                                .or(arrayElement(splitByChar(";", concat(s(""),";;;;;;")),7).ne(s(""))
                                        .and(arrayElement(splitByChar(";", concat("",s(";;;;;;;"))),8).ne(s("")))
                                        .and(lower(bar_code).ge(lower(arrayElement(splitByChar(";", concat(s(""),";;;;;;")),7))))
                                        .and(lower(bar_code).le(lower(arrayElement(splitByChar(";", concat("",s(";;;;;;;"))),8)))))
                                .or(arrayElement(splitByChar(";", concat(s(""),";;;;;;;;")),9).ne(s(""))
                                        .and(arrayElement(splitByChar(";", concat("",s(";;;;;;;;;"))),10).ne(s("")))
                                        .and(lower(bar_code).ge(lower(arrayElement(splitByChar(";", concat(s(""),";;;;;;;;")),9))))
                                        .and(lower(bar_code).le(lower(arrayElement(splitByChar(";", concat("",s(";;;;;;;;;"))),10)))))
                        ).and(toInt32(s("1000000")).eq(n32(1000000)).or(mass.ge(toInt32(s("0"))).and(mass.le(toInt32(s("1000000"))))))
                        .and(toInt32(s("1000000")).eq(n32(1000000)).or(price.ge(toInt32(s("0"))).and(price.le(toInt32(s("1000000"))))))
                        .and(toInt32(n8(-1)).eq(n32(-1)).or(If(toInt32(n8(-1)).eq(n32(0)),b(false),b(true))))
                )
                .groupby(n("index_from"), n("from"), n("type_from"), n("index_to"), n("to"), n("type_to"))
                .orderBy(count().desc())
                .limit(1000)
                .format(Format.TabSeparatedWithNamesAndTypes);


        System.out.println("query = \n" + PrintQuery.print(query));

        SelectQuery selectQuery = QueryOptimizer.simplifyExpressions(query, true, false);

        System.out.println("selectQuery = \n" + PrintQuery.print(selectQuery));


/*
SELECT
    if(toInt8(1) = -1, '', if(toInt8(1) = 1, '', if(toInt8(1) = 2, '', if(toInt8(1) = 3, '', if(toInt8(1) = 4, ops_from_code, ''))))) AS index_from,
    if(toInt8(1) = -1, '', if(toInt8(1) = 1, dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_from_code)), if(toInt8(1) = 2, dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_from_code)), if(toInt8(1) = 3, dictGetString('dim_fps_structure', 'post_object_no_index', toUInt64OrZero(ops_from_code)), if(toInt8(1) = 4, ops_from_code, ''))))) AS from,
    if(toInt8(-1) = -1, '', dictGetString('place_type', 'name', toUInt64(ops_from_type_code))) AS type_from,
    if(toInt8(1) = -1, '', if(toInt8(1) = 1, '', if(toInt8(1) = 2, '', if(toInt8(1) = 3, '', if(toInt8(1) = 4, ops_to_code, ''))))) AS index_to,
    if(toInt8(1) = -1, '', if(toInt8(1) = 1, dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_to_code)), if(toInt8(1) = 2, dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_to_code)), if(toInt8(1) = 3, dictGetString('dim_fps_structure', 'post_object_no_index', toUInt64OrZero(ops_to_code)), if(toInt8(1) = 4, ops_to_code, ''))))) AS to,
    if(toInt8(-1) = -1, '', dictGetString('place_type', 'name', toUInt64(ops_to_type_code))) AS type_to,
    count() AS amount,
    sum(forward_price) / 100. AS send_cost,
    sum(price) / 100. AS cost_size,
    sum(tax_price) / 100. AS cost_rate,
    sum(mass) / 1000. AS sum_weight,
    sum(index_count) AS number_of_nodes
FROM traffic_dist
WHERE ((toInt32(-1) = -1) OR if(toInt32(-1) = 0, 0, 1)) AND ((toInt32('1000000') = 1000000) OR ((price <= toInt32('1000000')) AND (price >= toInt32('0')))) AND ((toInt32('1000000') = 1000000) OR ((mass <= toInt32('1000000')) AND (mass >= toInt32('0')))) AND ((concat('', '') = '') OR ((lower(bar_code) LIKE lower(splitByChar(';', '')[1])) AND (splitByChar(';', '')[1] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';'))[2])) AND (splitByChar(';', concat('', ';'))[2] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;'))[3])) AND (splitByChar(';', concat('', ';;'))[3] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;;'))[4])) AND (splitByChar(';', concat('', ';;;'))[4] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;;;'))[4])) AND (splitByChar(';', concat('', ';;;;'))[4] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';'))[2])) AND (lower(bar_code) >= lower(splitByChar(';', '')[1])) AND (splitByChar(';', concat('', ';'))[2] != '') AND (splitByChar(';', '')[1] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;'))[4])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;'))[3])) AND (splitByChar(';', concat('', ';;;'))[4] != '') AND (splitByChar(';', concat('', ';;'))[3] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;'))[6])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;'))[5])) AND (splitByChar(';', concat('', ';;;;;'))[6] != '') AND (splitByChar(';', concat('', ';;;;'))[5] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;;;'))[8])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;;;'))[7])) AND (splitByChar(';', concat('', ';;;;;;;'))[8] != '') AND (splitByChar(';', concat('', ';;;;;;'))[7] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;;;;;'))[10])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;;;;;'))[9])) AND (splitByChar(';', concat('', ';;;;;;;;;'))[10] != '') AND (splitByChar(';', concat('', ';;;;;;;;'))[9] != ''))) AND (('' = '') OR (kpp LIKE concat('%', '', '%'))) AND (('' = '') OR (inn LIKE concat('%', '', '%'))) AND (('' = '') OR (returned_oper_date_time <= toDateTime('0000-00-00 00:00:00'))) AND (('' = '') OR (returned_oper_date_time >= toDateTime('0000-00-00 00:00:00'))) AND (('' = '') OR (accepted_oper_date_time <= toDateTime('0000-00-00 00:00:00'))) AND (('' = '') OR (accepted_oper_date_time >= toDateTime('0000-00-00 00:00:00'))) AND (('' = '') OR (delivered_oper_date_time <= toDateTime('0000-00-00 00:00:00'))) AND (('' = '') OR (delivered_oper_date_time >= toDateTime('0000-00-00 00:00:00'))) AND (('' = 'fps_to') OR ('fps_to' = 'fps_to') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_to_code)), ']') = 'fps_to') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_to_code)), '].[', dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_to_code)), ']') = 'fps_to') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_to_code)), '].[', dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_to_code)), '].[', dictGetString('dim_fps_structure', 'post_object', toUInt64OrZero(ops_to_code)), ']') = 'fps_to')) AND (('' = 'fps_from') OR ('fps_from' = 'fps_from') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_from_code)), ']') = 'fps_from') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_from_code)), '].[', dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_from_code)), ']') = 'fps_from') OR (concat('[FPS].[', dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_from_code)), '].[', dictGetString('dim_fps_structure', 'ufps', toUInt64OrZero(ops_from_code)), '].[', dictGetString('dim_fps_structure', 'post_object', toUInt64OrZero(ops_from_code)), ']') = 'fps_from')) AND (('' = 'direct_ctg') OR ('direct_ctg' = 'direct_ctg') OR (concat('[DirectCtg].[', dictGetString('direct_ctg', 'name', toUInt64(direct_ctg_code)), ']') = 'direct_ctg')) AND (('' = 'sender_ctg') OR ('sender_ctg' = 'sender_ctg') OR (concat('[SenderCtg].[', dictGetString('sender_ctg', 'value', toUInt64(send_ctg_code)), ']') = 'sender_ctg')) AND (('' = 'ops_to_type') OR ('ops_to_type' = 'ops_to_type') OR (concat('[OPSType].[', dictGetString('place_type', 'name', toUInt64(ops_to_type_code)), ']') = 'ops_to_type')) AND (('' = 'ops_from_type') OR ('ops_from_type' = 'ops_from_type') OR (concat('[OPSType].[', dictGetString('place_type', 'name', toUInt64(ops_from_type_code)), ']') = 'ops_from_type')) AND (('' = 'mail_ctg') OR ('mail_ctg' = 'mail_ctg') OR (concat('[Category].[', dictGetString('mailctg', 'name', toUInt64(mail_ctg_code)), ']') = 'mail_ctg')) AND (('' = 'mail_type') OR ('mail_type' = 'mail_type') OR (concat('[Type].[', dictGetString('mail_type', 'name', toUInt64(mail_type_code)), ']') = 'mail_type')) AND (('' = 'pay_type') OR ('pay_type' = 'pay_type') OR (concat('[Type].[', dictGetString('pay_type', 'name', toUInt64(pay_type)), ']') = 'pay_type'))
GROUP BY
    index_from,
    from,
    type_from,
    index_to,
    to,
    type_to
ORDER BY count() DESC
LIMIT 1000
FORMAT TabSeparatedWithNamesAndTypes



SELECT
    '' AS index_from,
    dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_from_code)) AS from,
    '' AS type_from,
    '' AS index_to,
    dictGetString('dim_fps_structure', 'macroregion', toUInt64OrZero(ops_to_code)) AS to,
    '' AS type_to,
    count() AS amount,
    sum(forward_price) / 100. AS send_cost,
    sum(price) / 100. AS cost_size,
    sum(tax_price) / 100. AS cost_rate,
    sum(mass) / 1000. AS sum_weight,
    sum(index_count) AS number_of_nodes
FROM traffic_dist
WHERE (concat('', '') = '') OR ((lower(bar_code) LIKE lower(splitByChar(';', '')[1])) AND (splitByChar(';', '')[1] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';'))[2])) AND (splitByChar(';', concat('', ';'))[2] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;'))[3])) AND (splitByChar(';', concat('', ';;'))[3] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;;'))[4])) AND (splitByChar(';', concat('', ';;;'))[4] != '')) OR ((lower(bar_code) LIKE lower(splitByChar(';', concat('', ';;;;'))[4])) AND (splitByChar(';', concat('', ';;;;'))[4] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';'))[2])) AND (lower(bar_code) >= lower(splitByChar(';', '')[1])) AND (splitByChar(';', concat('', ';'))[2] != '') AND (splitByChar(';', '')[1] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;'))[4])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;'))[3])) AND (splitByChar(';', concat('', ';;;'))[4] != '') AND (splitByChar(';', concat('', ';;'))[3] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;'))[6])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;'))[5])) AND (splitByChar(';', concat('', ';;;;;'))[6] != '') AND (splitByChar(';', concat('', ';;;;'))[5] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;;;'))[8])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;;;'))[7])) AND (splitByChar(';', concat('', ';;;;;;;'))[8] != '') AND (splitByChar(';', concat('', ';;;;;;'))[7] != '')) OR ((lower(bar_code) <= lower(splitByChar(';', concat('', ';;;;;;;;;'))[10])) AND (lower(bar_code) >= lower(splitByChar(';', concat('', ';;;;;;;;'))[9])) AND (splitByChar(';', concat('', ';;;;;;;;;'))[10] != '') AND (splitByChar(';', concat('', ';;;;;;;;'))[9] != ''))
GROUP BY
    index_from,
    from,
    type_from,
    index_to,
    to,
    type_to
ORDER BY count() DESC
LIMIT 1000
FORMAT TabSeparatedWithNamesAndTypes

*/

    }

}
