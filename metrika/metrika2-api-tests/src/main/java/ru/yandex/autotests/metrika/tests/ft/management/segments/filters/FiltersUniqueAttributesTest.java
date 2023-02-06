package ru.yandex.autotests.metrika.tests.ft.management.segments.filters;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nonParameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 02.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Граничные тесты на фильтр, не более 20-ти уникальных метрик и измерений в условиях")
public class FiltersUniqueAttributesTest {

    private static final int ATTRIBUTES_LIMIT = 20;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static Collection<String> metrics;

    private static final List<String> DIMENSIONS = asList(
            "ym:s:startURLPath",
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPath",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5",
            "ym:s:visitYear",
            "ym:s:visitMonth",
            "ym:s:visitDayOfMonth",
            "ym:s:firstVisitYear",
            "ym:s:firstVisitMonth",
            "ym:s:firstVisitDayOfMonth",
            "ym:s:totalVisits",
            "ym:s:pageViews",
            "ym:s:visitDuration",
            "ym:s:visits"
            );

    private Segment segment;
    private Long counterId;

    @BeforeClass
    public static void init() {
        metrics = user.onMetadataSteps().getMetrics(
                table(VISITS).and(nonParameterized())
                        .and(matches(not(equalTo("ym:s:affinityIndexInterests")))).and(matches(not(equalTo("ym:s:affinityIndexInterests2")))));

        assumeThat("для теста доступен список метрик", metrics,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));

        assumeThat("для теста доступен список измерений", DIMENSIONS,
                iterableWithSize(greaterThan(ATTRIBUTES_LIMIT)));
    }

    @Before
    public void setup() {
        segment = getDefaultSegment();

        CounterFull counter = new CounterFull()
                .withName(ManagementTestData.getCounterName())
                .withSite(ManagementTestData.getCounterSite());

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();
    }

    @Test
    public void maximumMetricsInFilter() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithAttributes(metrics, ATTRIBUTES_LIMIT));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(counterId, segment);
    }

    @Test
    public void moreThanMaximumMetricsInFilter() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithAttributes(metrics, ATTRIBUTES_LIMIT + 1));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ReportError.TOO_MANY_ATTRIBUTES_IN_FILTERS,
                counterId, segment);
    }

    @Test
    public void maximumDimensionsInFilter() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(counterId, segment);
    }

    @Test
    public void moreThanMaximumDimensionsInFilter() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithAttributes(DIMENSIONS, ATTRIBUTES_LIMIT + 1));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ReportError.TOO_MANY_ATTRIBUTES_IN_FILTERS,
                counterId, segment);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
