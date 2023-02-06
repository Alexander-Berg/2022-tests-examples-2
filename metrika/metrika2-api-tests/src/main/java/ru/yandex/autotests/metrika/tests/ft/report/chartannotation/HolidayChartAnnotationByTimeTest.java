package ru.yandex.autotests.metrika.tests.ft.report.chartannotation;

import com.google.common.collect.ImmutableMap;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.joda.time.LocalDate;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaReportChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.CHART_ANNOTATIONS})
@Title("Примечания на графиках: примечания по праздникам")
public class HolidayChartAnnotationByTimeTest {

    private static final String START_DATE = "2017-02-01";
    private static final String END_DATE = "2017-03-31";

    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = "ym:s:browser";

    private static final String TIME_ZONE = "Europe/Moscow";

    private static final Map<Integer, List<MetrikaReportChartAnnotation>> EXPECTED_ANNOTATIONS =
            ImmutableMap.<Integer, List<MetrikaReportChartAnnotation>>builder()
                    .put(22, of(new MetrikaReportChartAnnotation()
                            .withDate(new LocalDate(2017, 2, 23))
                            .withTitle("День защитника Отечества")
                            .withGroup(ChartAnnotationGroup.HOLIDAY)
                    ))
                    .put(23, of(new MetrikaReportChartAnnotation()
                            .withDate(new LocalDate(2017, 2, 24))
                            .withTitle("Перенос выходного с 01.01.2017")
                            .withGroup(ChartAnnotationGroup.HOLIDAY)
                    ))
                    .put(35, of(new MetrikaReportChartAnnotation()
                            .withDate(new LocalDate(2017, 3, 8))
                            .withTitle("Международный женский день")
                            .withGroup(ChartAnnotationGroup.HOLIDAY)
                    ))
                    .build();

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private Long counterId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()
                        .withTimeZoneName(TIME_ZONE)
                )
                .getId();
    }

    @Test
    public void test() {
        StatV1DataBytimeGETSchema response = user.onReportSteps().getBytimeReportAndExpectSuccess(
                new BytimeReportParameters()
                        .withId(counterId)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withMetric(METRIC)
                        .withDimension(DIMENSION)
                        .withGroup(GroupEnum.DAY)
                        .withIncludeAnnotations(true)
                        .withAnnotationGroups(of(ChartAnnotationGroup.HOLIDAY))
        );

        assertThat("Список примечаний соответствует ожиданию",
                response.getAnnotations(),
                getMatcher(response.getTimeIntervals().size())
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }

    private Matcher<Iterable<? extends List<MetrikaReportChartAnnotation>>> getMatcher(int intervalsSize) {
        return contains(
                IntStream.range(0, intervalsSize).mapToObj(i ->
                        EXPECTED_ANNOTATIONS.containsKey(i) ?
                                containsInAnyOrder(EXPECTED_ANNOTATIONS.get(i).stream()
                                        .map(BeanDifferMatcher::beanEquivalent)
                                        .collect(toList())
                                ) :
                                Matchers.<MetrikaReportChartAnnotation>emptyIterable()
                ).collect(toList())
        );
    }
}
