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

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;

/**
 * Created by konkov on 02.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Граничные тесты на фильтр, не более 10000 символов в строке в одном условии")
public class FiltersLengthOfConditionTest {

    private static final String CONDITION_DIMENSION = "ym:s:endURL";
    private static final int CONDITIONS_LENGTH_LIMIT = 10000;

    private static UserSteps user;

    private Segment segment;
    private Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
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
    public void maximumConditionLength() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(counterId, segment);
    }

    @Test
    public void moreThanMaximumConditionLength() {
        segment.setExpression(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT + 1));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ReportError.TOO_LONG_TERMS_IN_FILTERS,
                counterId, segment);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
