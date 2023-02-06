package ru.yandex.autotests.metrika.tests.ft.report.metrika.confidence;

import java.util.Collection;
import java.util.List;
import java.util.function.BiFunction;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
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
import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.isEmpty;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.nullValue;
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
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.cdp;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.interest2;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.metric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.offlineCalls;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.publishers;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.recommendationWidget;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.vacuum;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 16.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.CONFIDENCE)
@Title("Доверие к данным - отключение")
@RunWith(Parameterized.class)
public class ConfidenceDisableAttributesTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

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

    private static final Counter COUNTER_OFFLINE_CALLS = Counters.TEST_UPLOADINGS;
    private static final String START_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.START_DATE;
    private static final String END_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.END_DATE;

    private static final Counter COUNTER_PUBLISHERS = Counters.EUROPA_PLUS;
    private static final String START_DATE_PUBLISHERS = DateConstants.Publishers.START_DATE;
    private static final String END_DATE_PUBLISHERS = DateConstants.Publishers.END_DATE;

    private static final Counter COUNTER_YAN = Counters.YANDEX_NEWS;
    private static final String START_DATE_YAN = DateConstants.Yan.START_DATE;
    private static final String END_DATE_YAN = DateConstants.Yan.END_DATE;

    private static final String HIT_DIMENSION_NAME = "ym:pv:browser";
    private static final String VISIT_DIMENSION_NAME = "ym:s:browser";
    private static final String ADVERTISING_DIMENSION_NAME = "ym:ad:gender";

    private static final String INTEREST2_DATE = "2018-08-24";

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
        private String date1;
        private String date2;

        public FreeFormParameters getTail() {
            return tail;
        }

        public String getDimensionName() {
            return dimensionName;
        }

        public void setDimensionName(String dimensionName) {
            this.dimensionName = dimensionName;
        }

        public String getDate1() {
            return date1;
        }

        public Holder setDate1(String date1) {
            this.date1 = date1;
            return this;
        }

        public String getDate2() {
            return date2;
        }

        public Holder setDate2(String date2) {
            this.date2 = date2;
            return this;
        }

        public Holder withDimensionName(final String dimensionName) {
            this.dimensionName = dimensionName;
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
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, comparisonDateParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .vectorValues(MultiplicationBuilder.<MetricMetaExternal, String, Holder>builder(
                        user.onMetadataSteps().getMetricsMeta(x -> x.getDim().equals("ym:s:pageDepth")), Holder::new)
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
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.VISITS)),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            VISIT_DIMENSION_NAME : m.getRequiredDimension());
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
                        .apply(metric(table(TableEnum.VISITS).and(yan())),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            VISIT_DIMENSION_NAME : m.getRequiredDimension());
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER_YAN)
                                            .withAccuracy("0.1"));
                                    h.setDate1(START_DATE_YAN);
                                    h.setDate2(END_DATE_YAN);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(table(TableEnum.VISITS).and(interest2())),
                                (m, h) -> {
                                    h.setDimensionName(isEmpty(m.getRequiredDimension()) ?
                                            VISIT_DIMENSION_NAME : m.getRequiredDimension());
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER)
                                            .withAccuracy("0.1"));
                                    h.setDate1(INTEREST2_DATE);
                                    h.setDate2(INTEREST2_DATE);
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
                        .apply(metric(offlineCalls()),
                                (m, h) -> {
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER_OFFLINE_CALLS)
                                            .withAccuracy("1"));
                                    h.setDate1(START_DATE_OFFLINE_CALLS);
                                    h.setDate2(END_DATE_OFFLINE_CALLS);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(publishers()),
                                (m, h) -> {
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(COUNTER_PUBLISHERS)
                                            .withAccuracy("1"));
                                    h.setDate1(START_DATE_PUBLISHERS);
                                    h.setDate2(END_DATE_PUBLISHERS);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(vacuum()),
                                (m, h) -> {
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(Counters.YANDEX_EATS_ON_MAPS)
                                            .withAccuracy("1"));
                                    h.setDate1(DateConstants.Vacuum.START_DATE);
                                    h.setDate2(DateConstants.Vacuum.END_DATE);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(recommendationWidget()),
                                (m, h) -> {
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(Counters.YANDEX_WEATHER)
                                            .withAccuracy("0.001"));
                                    h.setDate1(DateConstants.RecommendationWidget.START_DATE);
                                    h.setDate2(DateConstants.RecommendationWidget.END_DATE);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(cdp()),
                                (m, h) -> {
                                    h.getTail().append(new CommonReportParameters()
                                            .withId(Counters.TEST_CDP)
                                            .withAccuracy("1"));
                                    h.setDate1(DateConstants.Cdp.START_DATE);
                                    h.setDate2(DateConstants.Cdp.END_DATE);
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(MetricMetaExternal::getDim))
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
                        .withMetric(metricName),
                new ConfidenceParameters()
                        .withWithConfidence(false),
                sort().by(holder.getDimensionName()));

        assumeThat("отчет содержит данные", result.getTotalRows(), greaterThanOrEqualTo(1L));
    }

    @Test
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkConfidenceFlags() {

        List<List<List<Boolean>>> confidenceFlags = result.getConfidenceFlags();

        assertThat("поле metrics_confidence_flags не содержит данных",
                confidenceFlags, everyItem(everyItem(everyItem(nullValue()))));
    }

    @Test
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkConfidenceThreshold() {

        List<List<List<Long>>> confidenceThresholds = result.getConfidenceThreshold();

        assertThat("поле metrics_confidence_threshold не содержит данных", confidenceThresholds,
                everyItem(everyItem(everyItem(nullValue()))));
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {anything(), anything(), equalTo("ym:s:pvlAll<offline_window>Window"), anything()},
                {anything(), anything(), equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {anything(), anything(), equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {anything(), anything(), containsString("adfox"), anything()}
        });
    }
}
