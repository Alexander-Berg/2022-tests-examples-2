package ru.yandex.autotests.metrika.tests.ft.report.metrika.confidence;

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
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
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

import java.util.Collection;
import java.util.List;
import java.util.function.BiFunction;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.StringUtils.isEmpty;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.comparisonDateParameters;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.dateParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 16.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.CONFIDENCE)
@Title("Доверие к данным, проверки исключения недостоверных данных при сортировке по метрике, поддерживающей режим доверия")
@RunWith(Parameterized.class)
public class ConfidenceExclusionTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = Counters.YANDEX_MARKET;
    private static final String START_DATE = "2016-06-20";
    private static final String END_DATE = "2016-06-30";

    private static final Counter COUNTER_ADVERTISING = Counters.IKEA_VSEM;
    private static final String START_DATE_ADVERTISING = DateConstants.Advertising.START_DATE;
    private static final String END_DATE_ADVERTISING = DateConstants.Advertising.END_DATE;

    private static final String HIT_DIMENSION_NAME = "ym:pv:browser";
    private static final String VISIT_DIMENSION_NAME = "ym:s:browser";
    private static final String ADVERTISING_DIMENSION_NAME = "ym:ad:gender";

    private Report result;
    private Report resultWithExclusions;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> dateParameters;

    @Parameterized.Parameter(2)
    public String metricName;

    @Parameterized.Parameter(3)
    public ConfidenceExclusionTest.Holder holder;

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

        public ConfidenceExclusionTest.Holder setDate1(String date1) {
            this.date1 = date1;
            return this;
        }

        public String getDate2() {
            return date2;
        }

        public ConfidenceExclusionTest.Holder setDate2(String date2) {
            this.date2 = date2;
            return this;
        }

        public ConfidenceExclusionTest.Holder withDate1(final String date1) {
            this.date1 = date1;
            return this;
        }

        public ConfidenceExclusionTest.Holder withDate2(final String date2) {
            this.date2 = date2;
            return this;
        }
    }

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, comparisonDateParameters()),
                        of(COMPARISON_DRILLDOWN, comparisonDateParameters()))
                .vectorValues(MultiplicationBuilder.<MetricMetaExternal, String, Holder>builder(
                        user.onMetadataSteps().getMetricsMeta(supportConfidence().and(metric(favorite().and(table(TableEnum.HITS)
                                .or(table(TableEnum.VISITS)
                                        .or(table(TableEnum.ADVERTISING))))))
                                .and(metric(not(equalTo("ym:s:sumParams"))))), Holder::new)
                        .apply(any(),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withId(COUNTER)
                                                    .withAccuracy("0.01"));
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
                        .apply(metric(parameterized(ParametrizationTypeEnum.GOAL_ID).and(table(TableEnum.ADVERTISING))),
                                (m, h) -> {
                                    m.setDim(new ParameterValues()
                                            .append(ParametrizationTypeEnum.GOAL_ID, String.valueOf(COUNTER_ADVERTISING.get(Counter.GOAL_ID)))
                                            .substitute(m.getDim()));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(parameterized(ParametrizationTypeEnum.GOAL_ID)),
                                (m, h) -> {
                                    m.setDim(new ParameterValues()
                                            .append(ParametrizationTypeEnum.GOAL_ID, String.valueOf(COUNTER.get(Counter.GOAL_ID)))
                                            .substitute(m.getDim()));
                                    return Stream.of(Pair.of(m, h));
                                })
                        //подставим валюту
                        .apply(metric(parameterized(ParametrizationTypeEnum.CURRENCY)),
                                (m, h) -> {
                                    m.setDim(new ParameterValues()
                                            .append(ParametrizationTypeEnum.CURRENCY, "RUB")
                                            .substitute(m.getDim()));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(metric(matches(startsWith("ym:ad:goal"))),
                                (m, h) -> {
                                    h.setDate1("2017-05-01");
                                    h.setDate2("2017-05-31");
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(MetricMetaExternal::getDim))
                .build();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.getDate1(), holder.getDate2()),
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withDimension(holder.dimensionName),
                new ConfidenceParameters()
                        .withWithConfidence(true)
                        .withExcludeInsignificant(false),
                sort().by(metricName).descending(),
                holder.getTail());

        assumeThat("отчет содержит данные", result.getTotalRows(), greaterThan(0L));

        resultWithExclusions = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                dateParameters.apply(holder.getDate1(), holder.getDate2()),
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withDimension(holder.dimensionName),
                new ConfidenceParameters()
                        .withWithConfidence(true)
                        .withExcludeInsignificant(true),
                sort().by(metricName).descending(),
                holder.getTail());

        assumeThat("отчет с режимом доверия содержит данные", resultWithExclusions.getTotalRows(), greaterThan(0L));
    }

    @Test
    public void checkConfidenceFlags() {
        List<List<Boolean>> confidenceFlags = result.getConfidenceFlags(metricName);

        assertThat("поле metrics_confidence_flags для сортируемой метрики содержит ожидаемое значение",
                confidenceFlags, everyItem(everyItem(either(equalTo(true)).or(equalTo(false)))));
    }

    @Test
    public void checkConfidenceFlagsWithExclusion() {
        List<List<Boolean>> confidenceFlags = resultWithExclusions.getConfidenceFlags(metricName);

        assertThat(
                "поле metrics_confidence_flags для сортируемой метрики c исключением недоверенных значений содержит ожидаемое значение",
                confidenceFlags, everyItem(everyItem(equalTo(true))));
    }

    @Test
    public void checkReportLength() {
        assertThat("результат без ненаежных данных содержит строк не больше, чем результат со всеми данными",
                result.getTotalRows(),
                greaterThanOrEqualTo(resultWithExclusions.getTotalRows()));
    }

    @Test
    public void checkExclusion() {
        /*
         извлекаем из результата запроса без исключения измерения у котороых флаг true
         извлекаем из результата запроса с исключениями все измерения
         проверяем что списки получились одинаковые
         */

        List<String> expectedDimensionValues = result.getDimensionWithConfidence(holder.getDimensionName(), metricName);
        List<String> actualDimensionValues = resultWithExclusions.getDimension(holder.getDimensionName());

        assertThat("строки исключены на основе флага доверия", actualDimensionValues,
                equalTo(expectedDimensionValues));
    }

}
