package ru.yandex.autotests.metrika.tests.ft.report.inpage.accuracy;

import java.util.Collection;
import java.util.List;
import java.util.Locale;
import java.util.stream.IntStream;
import java.util.stream.Stream;

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
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.reportwrappers.InpageReport;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.Math.exp;
import static java.lang.Math.log;
import static java.lang.Math.log10;
import static java.lang.Math.max;
import static java.lang.Math.round;
import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.closeTo;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_CLICK;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_FORM;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_LINK;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.INPAGE_SCROLL;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.getDecimalFormat;

/**
 * Created by sonick on 11.11.16.
 */
@Features(Requirements.Feature.INPAGE)
@Stories(Requirements.Story.Report.Parameter.ACCURACY)
@Title("Позитивные тесты на параметр accuracy в Inpage")
@RunWith(Parameterized.class)
public class InpageAccuracyPositiveTest {

    /**
     * MAX_EXPONENT и EPSILON задаются исходя из минимального значения коэффициента семплирования
     * min значение коэффициента семплирования после округления = 0.001
     */

    protected static final int MAX_EXPONENT = 3;
    protected static final int MAX_LINK_EXPONENT = 14;
    protected static final double EPSILON = 1e-4;
    private static final Collection<Double> ACCURACY_VALUES = of(
            1d, 0.5, 0.3, 0.15, 0.012, 0.018, 0.09, 0.099, 0.0101, 0.0001);
    private static final Collection<Double> LINK_ACCURACY_VALUES = of(
            1d, 0.5, 0.3, 0.15, 0.012, 0.018, 0.09, 0.099, 0.0101, 1e-15, 1e-16, 2e-15, 9e-16);

    protected static final String START_DATE = "3daysAgo";
    protected static final String END_DATE = "2daysAgo";
    protected static final int HEIGHT = 100;
    protected static final String URL = "https://metrika.yandex.ru/promo";
    protected static final String LINKURL = "https://metrika.yandex.ru/promo";

    private static final Counter COUNTER = YANDEX_METRIKA_2_0;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private InpageReport report;

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
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .vectorValues(
                                of(INPAGE_CLICK, new InpageDataParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withUrl(URL)),
                                of(INPAGE_FORM, new InpageDataParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withUrl(URL)),
                                of(INPAGE_SCROLL, new InpageDataParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withHeight(String.valueOf(HEIGHT))
                                        .withUrl(URL)))
                        .vectorValues(Stream
                                .of(
                                        getNumericParameters(MAX_EXPONENT),
                                        getMnemonicParameters(),
                                        getNumericParametersWithRounding(MAX_EXPONENT, ACCURACY_VALUES),
                                        getExponentNumericParameters(MAX_EXPONENT))
                                .flatMap(identity()))
                        .build())
                .addAll(CombinatorialBuilder.builder()
                        .vectorValues(
                                of(INPAGE_LINK, new InpageDataParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withUrl(LINKURL)))
                        .vectorValues(Stream
                                .of(
                                        getNumericParameters(MAX_LINK_EXPONENT),
                                        getMnemonicParameters(),
                                        getNumericParametersWithRounding(MAX_LINK_EXPONENT, LINK_ACCURACY_VALUES),
                                        getExponentNumericParameters(MAX_LINK_EXPONENT))
                                .flatMap(identity()))
                        .build())
                .build();
    }

    @Before
    public void setup() {
        report = user.onInpageSteps().getInpageReportAndExpectSuccess(
                requestType,
                parameters,
                new InpageDataParameters()
                        .withId(COUNTER)
                        .withAccuracy(accuracy));
    }

    @Test
    public void accuracyCheckSampleable() {

        Boolean expectedSampleable = !(report).getMaxSampleShare().equals(1.0);

        assertThat("признак использования семплирования, совпадает с ожидаемым",
                report.getSampleable(), equalTo(expectedSampleable));
    }

    @Test
    public void accuracyPositiveTest() {
        assertThat("доля данных, по которым осуществляется расчет, совпадает с ожидаемой",
                report.getSampleShare(), sampleShareMatcher);
    }

    private static Stream<List<Object>> getNumericParameters(int maxExponent) {
        return IntStream.range(1, maxExponent + 1)
                .mapToObj(exponent -> {
                    double accuracy = exp(-1 * exponent * log(10));
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
                .build();
    }

    private static Stream<List<Object>> getNumericParametersWithRounding(int maxExponent, Collection<Double> accuracyValues) {
        return accuracyValues.stream()
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
                    double accuracy = exp(-1 * exponent * log(10));
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
