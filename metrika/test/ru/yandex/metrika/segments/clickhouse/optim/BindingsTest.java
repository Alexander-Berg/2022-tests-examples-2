package ru.yandex.metrika.segments.clickhouse.optim;

import java.util.Optional;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.ast.SelectQuery;
import ru.yandex.metrika.segments.clickhouse.types.TBoolean;
import ru.yandex.metrika.segments.site.schema.MtLog;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Equals;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.If;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.ToString;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.concat;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.d;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.divide;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.greater;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.in;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.multiply;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.select;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.sum;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.toUInt16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un16s;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.un8;
import static ru.yandex.metrika.segments.site.bundles.AttributionUtils.attributed;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.ResolutionHeight;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.ResolutionWidth;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.StartDate;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickBannerID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickClientID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickContextType;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickIsGoodConversion;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickOrderID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickParentBannerID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickPhraseID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickPlaceID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ClickTargetPhraseID;
import static ru.yandex.metrika.segments.site.schema.MtLog.Visits.TrafficSource_ID;

/**
 * чем мы тут занимаемся.
 *
 * нам надо по выражению понять ограничения на его составные части.
 * например, в запросе во время его выполнения мы знаем что
 * 1) prewhere 1
 * 2) where 1
 * 3) arrayFilter(pred, args)
 *
 *
 * Created by orantius on 03.06.16.
 */
@Ignore
public class BindingsTest {

    private SelectQuery q;

    private QueryOptimizer queryOptimizer = new QueryOptimizer(true, new CardinalityEstimatorImpl(), false);

    @Before
    public void setUp() throws Exception {
        q = /*select(n("ym:ad:lastDirectPhraseOrCond").as("ym:ad:lastDirectPhraseOrCond"),
            If(s("").eq(n("ym:ad:lastDirectPhraseOrCondName")), n("ym:ad:lastDirectPhraseOrCondName2"), n("ym:ad:lastDirectPhraseOrCondName")).as("ym:ad:lastDirectPhraseOrCondNameInternal"),
            n("ym:ad:visits").as("ym:ad:visits"),
            n("ym:ad:users").as("ym:ad:users"),
            n("ym:ad:clicks").as("ym:ad:clicks"),
            greatest(n("ym:cs:uniqUpTo1LastDirectSearchPhrase"), n("ym:c:uniqUpTo1LastDirectSearchPhrase")))
        .from(
            select(concat(ToString(ContextType), ".",
                            If(ContextType.eq(un8(1)), ToString(PhraseID),
                                    If(ContextType.eq(un8(2)), ToString(PhraseID),
                                            If(ContextType.eq(un8(3)).or(ContextType.eq(un8(4))), s("0"),
                                                    If(ContextType.eq(un8(7)), ToString(TargetPhraseID), ToString(PhraseID) ))))).as("ym:ad:lastDirectPhraseOrCond"),
                    sum(MtLog.ClickStorage.Sign).as("ym:ad:clicks"))
            .from(MtLog.click_storage)
            .where(Date.eq(d("2016-05-30")).and(ClientID.eq(un32(2471038))).and(MtLog.ClickStorage.PlaceID.eq(n32(542))).and(MtLog.ClickStorage.GoodEvent.eq(n32(1))).and(ToString(MtLog.ClickStorage.OrderID).eq(s("2293202")))
                    .and(MtLog.ClickStorage.ParentBannerID.eq(un32(711213646)).and(MtLog.ClickStorage.ContextType.eq(un8(7)))
                            .or((MtLog.ClickStorage.BannerID.eq(un32(711213646)).and(MtLog.ClickStorage.ContextType.ne(un8(7)))))))
        ).globalAnyFullOuterJoin(*/
            select(concat(ToString(attributed(TrafficSource_ClickContextType,LAST)), ".",
                    If(attributed(TrafficSource_ClickContextType,LAST).eq(un8(1)), ToString(attributed(TrafficSource_ClickPhraseID,LAST)),
                            If(attributed(TrafficSource_ClickContextType,LAST).eq(un8(2)), ToString(attributed(TrafficSource_ClickPhraseID,LAST)),
                                    If(attributed(TrafficSource_ClickContextType,LAST).eq(un8(3)).or(attributed(TrafficSource_ClickContextType,LAST).eq(un8(4))), s("0"),
                                            If(attributed(TrafficSource_ClickContextType,LAST).eq(un8(7)), ToString(attributed(TrafficSource_ClickTargetPhraseID,LAST)), ToString(attributed(TrafficSource_ClickPhraseID,LAST)) ))))).as("ym:ad:lastDirectPhraseOrCond"),
                    sum(MtLog.Visits.Sign).as("ym:ad:visits"))
            .from(MtLog.visits_all)
                    .where(StartDate.eq(d("2016-05-30")).and(attributed(TrafficSource_ClickClientID,LAST).eq(un32(2471038))).and(ToString(attributed(TrafficSource_ClickOrderID,LAST)).eq(s("2293202")))
                            .and(attributed(TrafficSource_ClickPlaceID,LAST).in(ClickHouse.DIRECT_PLACE_IDS_n32)).and(attributed(TrafficSource_ClickIsGoodConversion,LAST)).and(attributed(TrafficSource_ID,LAST).eq(n8(3)))
                            .and(attributed(TrafficSource_ClickParentBannerID,LAST).eq(un64(711213646)).and(attributed(TrafficSource_ClickContextType,LAST).eq(un8(7)))
                                    .or(attributed(TrafficSource_ClickBannerID,LAST).eq(un64(711213646)).and(attributed(TrafficSource_ClickContextType,LAST).ne(un8(7))))))
        //).using(n("ym:ad:lastDirectPhraseOrCond"))
        .orderBy(n("ym:ad:users").desc(), n("ym:ad:lastDirectPhraseOrCond").asc())
        .limit(50).build();
/*

select `ym:ad:lastDirectPhraseOrCond` AS `ym:ad:lastDirectPhraseOrCond`,
    \'\' = `ym:ad:lastDirectPhraseOrCondName`?`ym:ad:lastDirectPhraseOrCondName2`:`ym:ad:lastDirectPhraseOrCondName` AS `ym:ad:lastDirectPhraseOrCondNameInternal`,
    `ym:ad:visits` AS `ym:ad:visits`, `ym:ad:users` AS `ym:ad:users`, `ym:ad:clicks` AS `ym:ad:clicks`,
    `ym:ad:643AdCost` AS `ym:ad:643AdCost`, `ym:ad:bounceRate` AS `ym:ad:bounceRate`,
    `ym:ad:pageDepth` AS `ym:ad:pageDepth`, `ym:ad:avgVisitDurationSeconds` AS `ym:ad:avgVisitDurationSeconds`,
    greatest(`ym:cs:uniqUpTo1LastDirectSearchPhrase`,`ym:c:uniqUpTo1LastDirectSearchPhrase`) AS `ym:ad:uniqUpTo1LastDirectSearchPhrase`
from (
        select concat(toString(ContextType),\'.\',ContextType = 1?toString(PhraseID):
                    (ContextType = 2?toString(PhraseID):
                    (ContextType = 3 OR ContextType = 4?\'0\':
                    (ContextType = 7?toString(TargetPhraseID):toString(PhraseID))))) AS `ym:ad:lastDirectPhraseOrCond`,
                max(ContextType = 1?dictGetStringOrDefault(\'phrases\',\'name\',toUInt64(PhraseID),toString(PhraseID)):
                    (ContextType = 2?concat(dictGetStringOrDefault(\'conditions\',\'name\',toUInt64(PhraseID),toString(PhraseID)),\' ({retargeting})\'):
                    (ContextType = 3 OR ContextType = 4?\'{auto_phrase}\':
                    (ContextType = 7?dictGetStringOrDefault(\'dynamic_conditions\',\'condition_name\',toUInt64(TargetPhraseID),toString(TargetPhraseID))
                        :toString(PhraseID))))) AS `ym:ad:lastDirectPhraseOrCondName`,
                sum(Sign) AS `ym:ad:clicks`,
                sum((CurrencyID = 643?CostCur / 1000000.0:0.0) * Sign) AS `ym:ad:643AdCost`,
                uniqUpToIf(1)(TargetType IN (0,2)?SearchPhrase:\'\',SearchPhrase != \'\' AND TargetType IN (0,2)) AS `ym:cs:uniqUpTo1LastDirectSearchPhrase`
            from click_storage
            where Date = toDate(\'2016-05-30\') and ClientID = 2471038 and PlaceID = 542 AND GoodEvent > 0 AND toString(OrderID) = \'2293202\'
                AND (ParentBannerID = 711213646 AND ContextType = 7 OR BannerID = 711213646 AND ContextType != 7)
            group by `ym:ad:lastDirectPhraseOrCond` with totals
) global any full outer join (
        select (PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1?concat(toString(ClickContextType),\'.\',
                    ClickContextType = 1?toString(ClickPhraseID):
                    (ClickContextType = 2?toString(ClickPhraseID):
                    (ClickContextType = 3 OR ClickContextType = 4?\'0\':
                    (ClickContextType = 7?toString(ClickTargetPhraseID):toString(ClickPhraseID))))):\'0.0\' AS `ym:ad:lastDirectPhraseOrCond`,
                max((PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1?((ClickOrderID IN (tuple(2293202,2975861)) AS _click_order_id_filter_)?
                    (ClickContextType = 1?dictGetStringOrDefault(\'phrases\',\'name\',toUInt64(ClickPhraseID),toString(ClickPhraseID)):
                    (ClickContextType = 2?concat(dictGetStringOrDefault(\'conditions\',\'name\',toUInt64(ClickPhraseID),toString(ClickPhraseID)),\' ({retargeting})\'):
                    (ClickContextType = 3 OR ClickContextType = 4?\'{auto_phrase}\':(ClickContextType = 7?dictGetStringOrDefault(\'dynamic_conditions\',\'condition_name\',toUInt64(ClickTargetPhraseID),
                            toString(ClickTargetPhraseID)):toString(ClickPhraseID))))):\'0.0\'):\'0.0\') AS `ym:ad:lastDirectPhraseOrCondName2`,
                sumIf(Sign,(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1) AS `ym:ad:visits`,
                uniqExactIf(UserID,(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1) AS `ym:ad:users`,
                100.0 * (sumIf(IsBounce * Sign,(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1) / `ym:ad:visits`) AS `ym:ad:bounceRate`,
                sumIf(PageViews * Sign,(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1) / `ym:ad:visits` AS `ym:ad:pageDepth`,
                sumIf(Duration * Sign,(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1) / `ym:ad:visits` AS `ym:ad:avgVisitDurationSeconds`,
                uniqUpToIf(1)(toInt64(ClickTargetType) IN (0,2)?(ClickSearchPhrase != \'\'?ClickSearchPhrase:SearchPhrase):\'\',(PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1
                                    AND (ClickSearchPhrase != \'\' AND ClickSearchPhrase != \'\' OR SearchPhrase != \'\' AND ClickSearchPhrase = \'\') AND toInt64(ClickTargetType) IN (0,2)) AS `ym:c:uniqUpTo1LastDirectSearchPhrase`
            from default.visits_layer
            where StartDate = toDate(\'2016-05-30\') and CounterID = 37496045 and ClickClientID = 2471038 AND toString(ClickOrderID) = \'2293202\'
                    AND (PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1 and toString(ClickOrderID) != \'0\'
                    AND (PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1 and (ClickParentBannerID = 711213646 AND ClickContextType = 7 OR ClickBannerID = 711213646 AND ClickContextType != 7)
                    AND (PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1 and
                        concat(toString(ClickContextType),\'.\',ClickContextType = 1?toString(ClickPhraseID):
                                (ClickContextType = 2?toString(ClickPhraseID):(ClickContextType = 3 OR ClickContextType = 4?\'0\':
                                (ClickContextType = 7?toString(ClickTargetPhraseID):toString(ClickPhraseID))))) != \'0.0\'
                    AND (PlaceID = 542 AND TraficSourceID = 3 AND ClickGoodEvent > 0) = 1
            group by `ym:ad:lastDirectPhraseOrCond` with totals
) using `ym:ad:lastDirectPhraseOrCond`
order by `ym:ad:users` desc, `ym:ad:lastDirectPhraseOrCond` asc
limit 50

*
* */
    }


    @Test
    public void testIf() {
        QueryOptimizer.MyExpressionTransformer selectTransformer = new QueryOptimizer.MyExpressionTransformer(false, false, Optional.empty(), Optional.empty());
        Expression<TBoolean> visit = Equals(
                If(greater(ResolutionHeight, un16(0)),
                        If(
                                in(toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)), un16s(9, 11, 12, 13, 14, 15, 16, 26, 28, 31, 33, 35, 37, 49)),
                                toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight)),
                                un16(0)),
                        un16(0)),
                un16(37))
                .visit(selectTransformer);
        // z = toUInt16(divide(multiply(ResolutionWidth, 21), ResolutionHeight))
        // RH>0 ? z in (...) ? z : 0 : 0 = 37
        // RH>0 && z in (...) ? z : 0  = 37
        // RH>0 && z in (...) && z = 37
        // RH>0 && z = 37
        System.out.println("res = " + visit);
    }

    @Test
    public void testOr() throws Exception {
        /*List<Expression<TBoolean>> res = QueryOptimizer.simplifyExpressions(Arrays.asList(
                greaterOrEquals(WindowClientWidth, WindowClientHeight),
                greater(WindowClientHeight, un16(0)),
                greater(WindowClientWidth, un16(0)),
                or(IsTablet, IsMobile)
        ), Optional.empty(), true);
        assertEquals(res.size(), 4);*/
    }


    @Test
    public void name() throws Exception {

        SelectQuery optimize = new QueryOptimizer(false, new CardinalityEstimatorImpl(), false).optimize(q);
        Expression<TBoolean> arg = optimize.getWhere().get();
        /*List<Expression<TBoolean>> res = QueryOptimizer.removeInsignificant(
                F.map(((FunctionCall<TBoolean>) arg).getArgs(), x -> (Expression<TBoolean>)x),
                Optional.empty(), true);*/

        System.out.println("arg = " + arg);
        //System.out.println("res = " + res);
        Bindings build = Bindings.build(arg, false);
        System.out.println("build = " + build);
        //build = Bindings{parent=null, bindings={
        // ClickClientID=DomainEq{in=true, elements=[2471038]},
        // ClickGoodEvent=DomainEq{in=true, elements=[1]},
        // StartDate=DomainEq{in=true, elements=[CHDate{dt='2016-05-30'}]},
        // toString(ClickOrderID)=DomainEq{in=true, elements=[2293202]},
        // ClickContextType=DomainEq{in=false, elements=[]},
        // TraficSourceID=DomainEq{in=true, elements=[3]},
        // PlaceID=DomainEq{in=true, elements=[542]}}}


    }
}
