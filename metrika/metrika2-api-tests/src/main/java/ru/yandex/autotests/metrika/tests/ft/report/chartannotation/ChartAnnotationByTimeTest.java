package ru.yandex.autotests.metrika.tests.ft.report.chartannotation;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.joda.time.DateTimeConstants;
import org.joda.time.Days;
import org.joda.time.LocalDate;
import org.joda.time.LocalTime;
import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.matchers.chartannotation.ChartAnnotationMatchers;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationUserGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaReportChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.IntStream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getDefaultAnnotation;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.CHART_ANNOTATIONS})
@Title("Примечания на графиках: примечания в отчете по времени")
@RunWith(Parameterized.class)
public class ChartAnnotationByTimeTest {

    private static final LocalDate START_DATE = new LocalDate(2017, 8, 1);
    private static final LocalDate END_DATE = new LocalDate(2017, 8, 31);

    private static final LocalDate BASE_DATE = new LocalDate(2017, 8, 12);
    private static final LocalTime BASE_TIME = new LocalTime(13, 55);

    private static final Integer DAYS_TO_END_DATE = Days.daysBetween(START_DATE, END_DATE).getDays();
    private static final Integer DAYS_TO_BASE_DATE = Days.daysBetween(START_DATE, BASE_DATE).getDays();

    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = "ym:s:browser";

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static Long counterId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Примечания выключены",
                        of(getDefaultAnnotation().withDate(BASE_DATE)),
                        new BytimeReportParameters(),
                        null
                ),
                toArray("Базовое примечание",
                        of(getDefaultAnnotation().withDate(BASE_DATE)),
                        new BytimeReportParameters()
                            .withGroup(GroupEnum.DAY)
                            .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Примечание в первый день периода",
                        of(getDefaultAnnotation().withDate(START_DATE)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        0
                ),
                toArray("Примечание в последний день периода",
                        of(getDefaultAnnotation().withDate(END_DATE)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        DAYS_TO_END_DATE
                ),
                toArray("Примечание до первого дня периода",
                        of(getDefaultAnnotation().withDate(START_DATE.minusDays(1))),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        -1
                ),
                toArray("Примечание после последнего дня периода",
                        of(getDefaultAnnotation().withDate(END_DATE.plusDays(1))),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        -1
                ),
                toArray("Примечание с группой A, группа выбрана явно",
                        of(getDefaultAnnotation().withDate(BASE_DATE).withGroup(ChartAnnotationUserGroup.A)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true)
                                .withAnnotationGroups(of(ChartAnnotationGroup.A, ChartAnnotationGroup.D)),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Примечание с группой A, группа не выбрана явно",
                        of(getDefaultAnnotation().withDate(BASE_DATE).withGroup(ChartAnnotationUserGroup.A)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true)
                                .withAnnotationGroups(of(ChartAnnotationGroup.B, ChartAnnotationGroup.C)),
                        -1
                ),
                toArray("Примечание с временем",
                        of(getDefaultAnnotation().withDate(BASE_DATE).withTime(BASE_TIME)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Примечание с временем в полночь",
                        of(getDefaultAnnotation().withDate(BASE_DATE).withTime(LocalTime.MIDNIGHT)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Примечание с временем перед полуночью",
                        of(getDefaultAnnotation()
                                .withDate(BASE_DATE)
                                .withTime(LocalTime.MIDNIGHT
                                        .hourOfDay().withMaximumValue()
                                        .minuteOfHour().withMaximumValue()
                                )
                        ),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Несколько примечаний в одном интервале",
                        of(
                                getDefaultAnnotation().withDate(BASE_DATE),
                                getDefaultAnnotation().withDate(BASE_DATE).withTime(BASE_TIME)
                        ),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.DAY)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE
                ),
                toArray("Базовое примечание, разбивка по часам",
                        of(getDefaultAnnotation().withDate(BASE_DATE)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.HOUR)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE * DateTimeConstants.HOURS_PER_DAY
                ),
                toArray("Примечание с временем, разбивка по часам",
                        of(getDefaultAnnotation().withDate(BASE_DATE).withTime(BASE_TIME)),
                        new BytimeReportParameters()
                                .withGroup(GroupEnum.HOUR)
                                .withIncludeAnnotations(true),
                        DAYS_TO_BASE_DATE * DateTimeConstants.HOURS_PER_DAY + BASE_TIME.getHourOfDay()
                )
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public List<MetrikaChartAnnotation> annotations;

    @Parameterized.Parameter(2)
    public BytimeReportParameters reportParameters;

    @Parameterized.Parameter(3)
    public Integer expectedIntervalIndex;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        annotations.forEach(annotation -> user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, annotation)
        );
    }

    @Test
    public void test() {
        StatV1DataBytimeGETSchema response = user.onReportSteps().getBytimeReportAndExpectSuccess(
                new BytimeReportParameters()
                        .withId(counterId)
                        .withDate1(START_DATE.toString())
                        .withDate2(END_DATE.toString())
                        .withMetric(METRIC)
                        .withDimension(DIMENSION),
                reportParameters
        );

        assertThat("Список примечаний соответствует ожиданию",
                response.getAnnotations(),
                getMatcher(response.getTimeIntervals().size())
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotations(counterId)
                .forEach(annotation -> user.onManagementSteps().onChartAnnotationSteps()
                        .deleteAnnotation(counterId, annotation.getId())
                );
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }

    private Matcher<Iterable<? extends List<MetrikaReportChartAnnotation>>> getMatcher(int intervalsSize) {
        return expectedIntervalIndex == null ? emptyIterable() : contains(
                IntStream.range(0, intervalsSize).mapToObj(i ->
                        expectedIntervalIndex == i ?
                                containsInAnyOrder(annotations.stream()
                                        .map(ChartAnnotationMatchers::matchesChartAnnotation)
                                        .collect(toList())
                                ) :
                                Matchers.<MetrikaReportChartAnnotation>emptyIterable()
                ).collect(toList())
        );
    }
}
