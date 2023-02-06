package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import java.util.Collection;
import java.util.Map;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static java.util.Collections.unmodifiableMap;
import static java.util.function.Function.identity;
import static java.util.stream.Collectors.toMap;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ROCKET_SALES;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.syntaxCdpUserCentric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;
import static ru.yandex.metrika.segments.core.meta.segment.UserFilterType.METRIC;

public class CdpUserCentricFiltersMetricB2bTest extends BaseB2bTest {
    protected static final Counter COUNTER = ROCKET_SALES;
    protected static final String START_DATE = "2021-05-19";
    protected static final String END_DATE = "2021-05-27";

    private static final String FILTER_START_SPECIAL_DATE = "2021-05-19";
    private static final String FILTER_END_SPECIAL_DATE = "2021-05-27";

    private static final Map<String, Expression> FILTERS = unmodifiableMap(Stream.of(
            Pair.of("ym:u:cdpOrdersCount", dimension("ym:u:cdpOrdersCount").lessThan(10)),
            Pair.of("ym:u:cdpPayedOrdersCount", dimension("ym:u:cdpPayedOrdersCount").lessThan(10)),
            Pair.of("ym:u:cdpCancelledOrdersCount", dimension("ym:u:cdpCancelledOrdersCount").lessThan(10)),
            Pair.of("ym:u:cdp<currency>AvgCheck", dimension("ym:u:cdpRUBAvgCheck").lessThan(10)),
            Pair.of("ym:u:cdp<currency>TotalRevenue", dimension("ym:u:cdpRUBTotalRevenue").lessThan(10)),
            Pair.of("ym:u:cdp<currency>TotalProfit", dimension("ym:u:cdpRUBTotalProfit").lessThan(10)),
            Pair.of("ym:u:cdpSpamOrdersExists", dimension("ym:u:cdpSpamOrdersExists").equalTo("No")),

            // параметры которые нужно заигнорить
            Pair.of("ym:u:goalReaches", dimension("ym:u:goal<goal_id>Reaches").notDefined()),
            Pair.of("ym:u:goalVisits", dimension("ym:u:goal<goal_id>Visits").notDefined()),
            Pair.of("ym:u:pageViews", dimension("ym:u:pageViews").notDefined()),
            Pair.of("ym:u:totalVisitsDuration", dimension("ym:u:totalVisitsDuration").notDefined()),
            Pair.of("ym:u:userVisits", dimension("ym:u:userVisits").notDefined()),
            Pair.of("ym:u:productViews", dimension("ym:u:productViews").notDefined()),
            Pair.of("ym:u:purchaseNumber", dimension("ym:u:purchaseNumber").notDefined()),
            Pair.of("ym:u:productsBought", dimension("ym:u:productsBought").notDefined()),
            Pair.of("ym:u:userRevenue", dimension("ym:u:userRevenue").notDefined()),
            Pair.of("ym:u:user<currency>Revenue", dimension("ym:u:userRUBRevenue").notDefined()),
            Pair.of("ym:u:productsAdded", dimension("ym:u:productsAdded").notDefined()),
            Pair.of("ym:u:userOfflineCalls", dimension("ym:u:userOfflineCalls").notDefined())
    ).collect(toMap(Pair::getKey, Pair::getValue)));

    public IFormParameters dateFilterParameters;

    @Parameterized.Parameter()
    public Expression filter;

    @Parameterized.Parameter(1)
    public String metricName;

    @Parameterized.Parameter(2)
    public UserCentricParamsHolder userCentricParamsHolder;

    @Parameterized.Parameters(name = "фильтр {0} метрика {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(userOnTest.onUserCentricMetadataSteps().getFilters(METRIC, FILTERS, FILTER_START_SPECIAL_DATE, FILTER_END_SPECIAL_DATE))
                .vectorValues(MultiplicationBuilder.<String, String, UserCentricParamsHolder>builder(
                        userOnTest.onMetadataSteps().getMetrics(syntaxCdpUserCentric()), UserCentricParamsHolder::new)
                        .apply(any(),
                                (d, h) -> {
                                    h.setCounter(COUNTER);
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.VISITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(userOnTest.onMetadataSteps()
                                                            .getDimensions(syntaxCdpUserCentric().and(table(TableEnum.VISITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.HITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(userOnTest.onMetadataSteps()
                                                            .getDimensions(syntaxCdpUserCentric().and(table(TableEnum.HITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Override
    public void check() {
        Object referenceBean = userOnRef.onReportSteps().getRawReport(
                requestType,
                dateFilterParameters,
                reportParameters,
                userCentricParamsHolder.getTail());
        Object testingBean = userOnTest.onReportSteps().getRawReport(
                requestType,
                dateFilterParameters,
                reportParameters,
                userCentricParamsHolder.getTail());

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, beanEquivalent(referenceBean).fields(getIgnore()).withVariation(doubleWithAccuracy));
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }

    protected IFormParameters getReportParameters() {
        return aggregate(goalId(userCentricParamsHolder.getCounter()),
                new CommonReportParameters()
                        .withId(userCentricParamsHolder.getCounter().get(ID))
                        .withMetric(metricName));
    }

    @IgnoreParameters.Tag(name = "no data")
    public static Collection<Object[]> ignoreParametersNoData() {
        return asList(new Object[][]{
                // для этих аттрибутов нет данных
                {having(on(Expression.class).build(), containsString("ym:u:userVisits")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:goal<goal_id>Reaches")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:goal<goal_id>Visits")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:pageViews")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:totalVisitsDuration")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:productViews")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:purchaseNumber")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:productsBought")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:userRevenue")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:userRUBRevenue")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:productsAdded")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:userOfflineCalls")), anything(), anything()}
        });
    }
}
