package ru.yandex.autotests.metrika.tests.ft.report.metrika.ids;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
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
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.NOTIK;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.WIKIMART_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 14.10.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.IDS})
@Title("Отчет 'таблица': отчет для группы счетчиков")
@RunWith(Parameterized.class)
public class TableIdsTest {

    private static final Counter COUNTER1 = WIKIMART_RU;
    private static final Counter COUNTER2 = NOTIK;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

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
    public String endDate;

    @Parameterized.Parameter(5)
    public String metricName;

    @Parameterized.Parameter(6)
    public TableIdsTest.Holder holder;

    private static final class Holder {
        private FreeFormParameters tail = makeParameters();

        public FreeFormParameters getTail() {
            return tail;
        }
    }

    @Parameterized.Parameters(name = "{0}, метрика: {5}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters(), simpleMetricExtractor()),
                        of(DRILLDOWN, dateParameters(), simpleMetricExtractor()),
                        of(COMPARISON, segmentAdateParameters(), segmentAMetricExtractor()),
                        of(COMPARISON, segmentBdateParameters(), segmentBMetricExtractor()),
                        of(COMPARISON_DRILLDOWN, segmentAdateParameters(), segmentAMetricExtractor()),
                        of(COMPARISON_DRILLDOWN, segmentBdateParameters(), segmentBMetricExtractor()),
                        of(BY_TIME, byTimeDateParameters(), simpleMetricExtractor()))
                .vectorValues(of("2017-05-15", "2017-05-15"))
                .vectorValues(MultiplicationBuilder.<String, String, TableIdsTest.Holder>builder(
                        user.onMetadataSteps().getMetrics(non_unigue().and(table(TableEnum.ADVERTISING).negate())
                                .and(matches(not(startsWith("ym:s:goal"))))), Holder::new)
                        .apply(any(),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withAccuracy("1"));
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
                        .withMetric(metricName)
                        .withIds(COUNTER1),
                parameters.apply(startDate, endDate));

        secondPart = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withIds(COUNTER2),
                parameters.apply(startDate, endDate));

        bothParts = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                holder.getTail(),
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withIds(COUNTER1, COUNTER2),
                parameters.apply(startDate, endDate));
    }

    @Test
    public void checkMetricValue() {
        Double firstCounterMetric = metricExtractor.apply(firstPart);
        Double secondCounterMetric = metricExtractor.apply(secondPart);
        Double bothCountersMetric = metricExtractor.apply(bothParts);

        assertThat(
                "значение метрики в отчете по группе счетчиков совпадает суммой значений в отдельных отчетах",
                bothCountersMetric, equalTo(firstCounterMetric + secondCounterMetric));
    }

    private static Function<Report, Double> simpleMetricExtractor() {
        return report -> report.getMetrics().size() != 0 ? report.getMetrics().get(0).get(0).get(0) : 0D;
    }

    private static Function<Report, Double> segmentAMetricExtractor() {
        return report -> report.getMetrics().size() != 0 ? report.getMetrics().get(0).get(0).get(0) : 0D;
    }

    private static Function<Report, Double> segmentBMetricExtractor() {
        return report -> report.getMetrics().size() != 0 ? report.getMetrics().get(0).get(1).get(0) : 0D;
    }
}
