package ru.yandex.autotests.metrika.tests.ft.report.metrika.accuracy;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.Locale;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.Math.*;
import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.getDecimalFormat;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.ACCURACY)
@Title("Позитивные тесты на параметр accuracy")
@RunWith(Parameterized.class)
public class AccuracyPositiveTest {
    private static final Counter COUNTER = Counters.YANDEX_MARKET;

    private static final int MAX_EXPONENT = 14;
    private static final double EPSILON = 1e-15;
    private static final Collection<Double> ACCURACY_VALUES = of(
            1d, 0.5, 0.3, 0.15, 0.012, 0.018, 0.09, 0.099, 0.0101, 1e-15, 1e-16, 2e-15, 9e-16);

    private static final String START_DATE = "2014-09-01";
    private static final String END_DATE = "2014-09-02";
    private static final String DIMENSION_NAME = "ym:s:age";
    private static final String METRIC_NAME = "ym:s:visits";

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private Report report;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String accuracy;

    @Parameterized.Parameter(3)
    public Matcher<?> sampleShareMatcher;

    @Parameterized.Parameters(name = "{0}; accuracy={2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(BY_TIME, new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(TABLE, new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(DRILLDOWN, new DrillDownReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(COMPARISON, new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)))
                .vectorValues(Stream
                        .of(
                                getNumericParameters(MAX_EXPONENT),
                                getMnemonicParameters(),
                                getNumericParametersWithRounding(MAX_EXPONENT),
                                getExponentNumericParameters(MAX_EXPONENT))
                        .flatMap(identity()))
                .build();

    }

    @Before
    public void setup() {
        report = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                parameters,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withAccuracy(accuracy));
    }

    @Test
    public void accuracyCheckSampled() {

        Boolean expectedSampled = !report.getSampleSize().equals(report.getSampleSpace());

        assertThat("признак использования семплирования, совпадает с ожидаемым",
                report.getSampled(), equalTo(expectedSampled));
    }

    @Test
    public void accuracyCheckSampleShare() {

        Double sampleShare = report.getSampleShare();
        Long sampleSpace = report.getSampleSpace();
        Long expectedSampleSize = round(sampleShare * sampleSpace);

        assertThat("количество строк в выборке данных совпадает с ожидаемым",
                report.getSampleSize(), equalTo(expectedSampleSize));
    }

    @Test
    public void accuracyPositiveTest() {
        assertThat("доля данных, по которым осуществляется расчет, совпадает с ожидаемой",
                report.getSampleShare(), sampleShareMatcher);
    }

    private static Stream<List<Object>> getNumericParameters(int maxExponent) {
        return IntStream.range(1, maxExponent + 1)
                .mapToObj(exponent -> {
                    Double accuracy = exp(-1 * exponent * log(10));
                    return ImmutableList.builder()
                            .add(getDecimalFormat(maxExponent).format(accuracy))
                            .add(closeTo(accuracy, EPSILON))
                            .build();
                });
    }

    private static Stream<List<Object>> getMnemonicParameters() {
        return Stream.<List<Object>>builder()
                .add(asList(null, anything()))
                .add(asList("low", anything()))
                .add(asList("medium", anything()))
                .add(asList("high", anything()))
                .add(asList("full", anything()))
                .build();
    }

    private static Stream<List<Object>> getNumericParametersWithRounding(int maxExponent) {
        return ACCURACY_VALUES.stream()
                .map(value -> {
                    Double sampleShare = getExpectedSampleShare(maxExponent, value);
                    return ImmutableList.builder()
                            .add(getDecimalFormat(2 * maxExponent).format(value))
                            .add(closeTo(sampleShare, EPSILON))
                            .build();
                });
    }

    private static Stream<List<Object>> getExponentNumericParameters(int maxExponent) {
        return IntStream.range(1, maxExponent + 1)
                .mapToObj(exponent -> {
                    Double accuracy = exp(-1 * exponent * log(10));
                    return ImmutableList.builder()
                            .add(String.format(Locale.ROOT, "%.0e", accuracy))
                            .add(closeTo(accuracy, EPSILON))
                            .build();
                });
    }

    private static Double getExpectedSampleShare(int maxExponent, Double value) {
        long index = round(log10(1 / value));
        double sampleShare = exp(-1 * index * log(10));
        double minimumSampleShare = exp(-1 * maxExponent * log(10));
        return max(sampleShare, minimumSampleShare);
    }

}
