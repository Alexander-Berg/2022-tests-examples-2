package ru.yandex.autotests.metrika.tests.ft.report.metrika.confidence;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ConfidenceParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.Math.max;
import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.StringUtils.isEmpty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.COMPARISON;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.COMPARISON_DRILLDOWN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.DRILLDOWN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.autotests.metrika.utils.Utils.replaceParameters;

/**
 * Created by konkov on 17.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.CONFIDENCE)
@Title("Доверие к данным, значение флага доверия к данным, метрики по кликам Директа")
@RunWith(Parameterized.class)
public class ConfidenceThresholdTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = Counters.YANDEX_MARKET;
    private static final String START_DATE = "2015-06-20";
    private static final String END_DATE = "2015-06-20";

    private static final Counter COUNTER_ECOMMERCE = Counters.ECOMMERCE_TEST;
    private static final String START_DATE_ECOMMERCE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE_ECOMMERCE = DateConstants.Ecommerce.END_DATE;

    private static final Counter COUNTER_ADVERTISING = Counters.IKEA_VSEM;
    private static final String START_DATE_ADVERTISING = DateConstants.Advertising.START_DATE;
    private static final String END_DATE_ADVERTISING = DateConstants.Advertising.END_DATE;

    private static final String HIT_DIMENSION_NAME = "ym:pv:browser";
    private static final String VISIT_DIMENSION_NAME = "ym:s:browser";
    private static final String ADVERTISING_DIMENSION_NAME = "ym:ad:gender";

    private static final String HIT_THRESHOLD_METRIC_NAME = "ym:pv:pageviews";
    private static final String VISIT_THRESHOLD_METRIC_NAME = "ym:s:visits";

    /**
     * дополнительный порог см. https://st.yandex-team.ru/METR-18638#1447244924000
     */
    public static final double UNCONDITIONAL_THRESHOLD = 24;

    private Report result;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public String metricName;

    @Parameterized.Parameter(3)
    public Holder holder;

    static class Holder {
        private FreeFormParameters tail = makeParameters();
        private String dimensionName;
        private String thresholdMetricName;
        private String date1;
        private String date2;

        public FreeFormParameters getTail() {
            return tail;
        }

        public void setTail(FreeFormParameters tail) {
            this.tail = tail;
        }

        public String getDimensionName() {
            return dimensionName;
        }

        public void setDimensionName(String dimensionName) {
            this.dimensionName = dimensionName;
        }

        public String getThresholdMetricName() {
            return thresholdMetricName;
        }

        public void setThresholdMetricName(String thresholdMetricName) {
            this.thresholdMetricName = thresholdMetricName;
        }

        public String getDate1() {
            return date1;
        }

        public void setDate1(String date1) {
            this.date1 = date1;
        }

        public String getDate2() {
            return date2;
        }

        public void setDate2(String date2) {
            this.date2 = date2;
        }

        public Holder withDimensionName(final String dimensionName) {
            this.dimensionName = dimensionName;
            return this;
        }

        public Holder withThresholdMetricName(final String thresholdMetricName) {
            this.thresholdMetricName = thresholdMetricName;
            return this;
        }

        public Holder withDate1(final String date1) {
            this.date1 = date1;
            return this;
        }

        public Holder withDate2(final String date2) {
            this.date2 = date2;
            return this;
        }
    }

    @Parameterized.Parameters(name = "{0} метрика {2}")
    public static Collection<Object[]> createParameters() {
        Map<String, String> advertisingThresholdMetrics = user.onMetadataSteps().getThresholdAdvertisingMetrics();

        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, comparisonDateParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .vectorValues(MultiplicationBuilder.<MetricMetaExternal, String, Holder>builder(
                                user.onMetadataSteps().getMetricsMeta(metric(
                                        table(TableEnum.HITS)
                                                .or(table(TableEnum.VISITS)
                                                        .or(table(TableEnum.ADVERTISING)))).and(supportConfidence())
                                        .and(favoriteMetrics())),
                                Holder::new)
                        .apply(any(),
                                (m, h) -> {
                                    h.getTail().append(
                                                    new CommonReportParameters()
                                                            .withId(COUNTER)
                                                            .withAccuracy("0.01"))
                                            .append(currency("RUB"));
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.HITS)),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            HIT_DIMENSION_NAME : m.getRequiredDimension());
                                    h.setThresholdMetricName(HIT_THRESHOLD_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.VISITS)),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            VISIT_DIMENSION_NAME : m.getRequiredDimension());
                                    h.setThresholdMetricName(VISIT_THRESHOLD_METRIC_NAME);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.VISITS).and(ecommerce())),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            VISIT_DIMENSION_NAME : m.getRequiredDimension());
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER_ECOMMERCE)
                                            .withAccuracy("1"));
                                    h.setDate1(START_DATE_ECOMMERCE);
                                    h.setDate2(END_DATE_ECOMMERCE);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.ADVERTISING)),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            ADVERTISING_DIMENSION_NAME : m.getRequiredDimension());
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER_ADVERTISING)
                                            .withDirectClientLogins(
                                                    user.onManagementSteps().onClientSteps().getClientLogins(
                                                            new ClientsParameters()
                                                                    .withCounters(COUNTER_ADVERTISING)
                                                                    .withDate1(START_DATE_ADVERTISING)
                                                                    .withDate2(END_DATE_ADVERTISING),
                                                            ulogin(COUNTER_ADVERTISING))));
                                    h.setDate1(START_DATE_ADVERTISING);
                                    h.setDate2(END_DATE_ADVERTISING);
                                    h.setThresholdMetricName(advertisingThresholdMetrics.get(m.getDim()));
                                    return Stream.of(Pair.of(m, h));
                                })
                        //подставим goal_id
                        .apply(metric(parameterized(ParametrizationTypeEnum.GOAL_ID)),
                                (m, h) -> {
                                    h.getTail().append(goalId(COUNTER));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(parameterized(ParametrizationTypeEnum.GOAL_ID).and(ecommerce())),
                                (m, h) -> {
                                    h.getTail().append(goalId(COUNTER_ECOMMERCE));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.ADVERTISING).and(parameterized(ParametrizationTypeEnum.GOAL_ID))),
                                (m, h) -> {
                                    h.getTail().append(goalId(COUNTER_ADVERTISING));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(cdp()), (m, h) -> {
                            h.setDate1(DateConstants.Cdp.START_DATE);
                            h.setDate2(DateConstants.Cdp.END_DATE);
                            h.getTail()
                                    .append(new CommonReportParameters()
                                            .withId(TEST_CDP)
                                            .withAccuracy("1"));
                            return Stream.of(Pair.of(m, h));
                        })
                        .apply(metric(vacuum()),
                                (m, h) -> Stream.empty())
                        .buildVectorValues(MetricMetaExternal::getDim)
                )
                .build();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                dateParameters.apply(holder.getDate1(), holder.getDate2()),
                new CommonReportParameters()
                        .withDimension(holder.getDimensionName())
                        .withMetrics(of(metricName, holder.getThresholdMetricName())),
                new ConfidenceParameters()
                        .withWithConfidence(true)
                        .withExcludeInsignificant(false),
                sort().by(holder.getDimensionName()));

        assumeThat("отчет содержит данные", result.getTotalRows(), greaterThanOrEqualTo(1L));
    }

    @Test
    public void checkConfidenceFlag() {

        List<List<Double>> metricThreshold = result.getMetric(holder.getThresholdMetricName());
        List<List<Boolean>> confidenceFlags = result.getConfidenceFlags(
                replaceParameters(metricName, holder.getTail()));
        List<List<Long>> confidenceThresholds = result.getConfidenceThreshold(
                replaceParameters(metricName, holder.getTail()));

        List<List<Boolean>> expectedConfidenceFlags = IntStream.range(0, confidenceFlags.size())
                .mapToObj(indx -> singletonList(metricThreshold.get(indx).get(0) >=
                        max(confidenceThresholds.get(indx).get(0), UNCONDITIONAL_THRESHOLD)))
                .collect(toList());

        assertThat("значение поля metrics_confidence_flags совпадает с ожидаемым", confidenceFlags,
                equalTo(expectedConfidenceFlags));
    }
}
