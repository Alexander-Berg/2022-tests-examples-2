package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.matchers.Matchers.closeTo;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.DATE)
@Title("Период выборки")
@RunWith(Parameterized.class)
public class DateTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = CounterConstants.LITE_DATA;
    private static final Counter COUNTER_ADVERTISING = Counters.IKEA_VSEM;
    private static final Counter COUNTER_SUM_PARAMS = Counters.TEST_SUM_PARAMS;

    private Report firstPart;
    private Report secondPart;
    private Report bothParts;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> parameters;

    @Parameterized.Parameter(2)
    public Function<Report, Double> metricExtractor;

    @Parameterized.Parameter(3)
    public String startDate;

    @Parameterized.Parameter(4)
    public String midEndDate;

    @Parameterized.Parameter(5)
    public String midStartDate;

    @Parameterized.Parameter(6)
    public String endDate;

    @Parameterized.Parameter(7)
    public String metricName;

    @Parameterized.Parameter(8)
    public Holder holder;

    private static final class Holder {
        private FreeFormParameters tail = makeParameters();
        private double tolerance = 0d;

        public FreeFormParameters getTail() {
            return tail;
        }

        public double getTolerance() {
            return tolerance;
        }

        public void setTolerance(double tolerance) {
            this.tolerance = tolerance;
        }
    }

    @Parameterized.Parameters(name = "{0} {7} {3}:{4} {5}:{6}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters(), simpleMetricExtractor()),
                        of(DRILLDOWN,  dateParameters(), simpleMetricExtractor()),
                        of(COMPARISON, segmentAdateParameters(), segmentAMetricExtractor()),
                        of(COMPARISON, segmentBdateParameters(), segmentBMetricExtractor()),
                        of(COMPARISON_DRILLDOWN, segmentAdateParameters(), segmentAMetricExtractor()),
                        of(COMPARISON_DRILLDOWN, segmentBdateParameters(), segmentBMetricExtractor()),
                        of(BY_TIME, byTimeDateParameters(), simpleMetricExtractor()))
                .vectorValues(
                        of("2016-02-01", "2016-02-01", "2016-02-02", "2016-02-02"),
                        of("5daysAgo", "4daysAgo", "3daysAgo", "2daysAgo"),
                        of("4daysAgo", "3daysAgo", "2daysAgo", "yesterday"),
                        asList(null, "5daysAgo", "4daysAgo", "3daysAgo"))
                .vectorValues(MultiplicationBuilder.<String, String, Holder>builder(
                        user.onMetadataSteps().getMetrics(favorite().and(non_unigue())), Holder::new)
                        .apply(any(),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(COUNTER)
                                                    .withAccuracy("1"));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.VISITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(COUNTER.get(ID)),
                                            goalId(3176500L)); //ID цели захардкожен, чтобы не ломать другие тесты
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.ADVERTISING),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(COUNTER_ADVERTISING)
                                                    .withDirectClientLogins(
                                                            user.onManagementSteps().onClientSteps().getClientLogins(
                                                                    new ClientsParameters()
                                                                            .withCounters(COUNTER_ADVERTISING.get(ID)),
                                                                    ulogin(COUNTER_ADVERTISING.get(U_LOGIN)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(matches(equalTo("ym:dl:downloads")),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(Counters.GENVIC_RU));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(matches(equalTo("ym:s:sumParams")),
                                (m, h) -> {
                                    h.setTolerance(0.0001d);
                                    h.getTail().append(
                                        new CommonReportParameters().withId(COUNTER_SUM_PARAMS),
                                            goalId(COUNTER_SUM_PARAMS.get(Counter.GOAL_ID)));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Before
    public void setup() {
        firstPart = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                new CommonReportParameters()
                        .withMetric(metricName),
                parameters.apply(startDate, midEndDate));

        secondPart = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                new CommonReportParameters()
                        .withMetric(metricName),
                parameters.apply(midStartDate, endDate));

        bothParts = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                new CommonReportParameters()
                        .withMetric(metricName),
                parameters.apply(startDate, endDate));
    }

    @Test
    public void checkMetricValue() {

        Double firstPartMetric = metricExtractor.apply(firstPart);
        Double secondPartMetric = metricExtractor.apply(secondPart);
        Double bothPartsMetric = metricExtractor.apply(bothParts);

        assertThat(
                "сумма значений метрики в смежных интервалах совпадает со значеним метрики в объединенном интервале",
                bothPartsMetric,
                getMatcher(firstPartMetric + secondPartMetric)
        );
    }

    private Matcher<Double> getMatcher(Double expected) {
        if (holder.getTolerance() == 0d) {
            return equalTo(expected);
        } else {
            return closeTo(expected, holder.getTolerance(), true);
        }
    }

    private static Function<Report, Double> simpleMetricExtractor() {
        return report -> report.getMetrics().get(0).get(0).get(0);
    }

    private static Function<Report, Double> segmentAMetricExtractor() {
        return report -> report.getMetrics().get(0).get(0).get(0);
    }

    private static Function<Report, Double> segmentBMetricExtractor() {
        return report -> report.getMetrics().get(0).get(1).get(0);
    }
}
