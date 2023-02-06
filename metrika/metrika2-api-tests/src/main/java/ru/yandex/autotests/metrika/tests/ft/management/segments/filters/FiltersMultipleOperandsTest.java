package ru.yandex.autotests.metrika.tests.ft.management.segments.filters;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.filters.Operator;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;

/**
 * Created by konkov on 02.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Граничные тесты на фильтр, не более 100 операндов в одном операторе")
@RunWith(Parameterized.class)
public class FiltersMultipleOperandsTest {

    private static final String DIMENSION_NAME = "ym:s:pageViews";
    private static final int MAXIMUM_OPERANDS = 100;

    private static UserSteps user;

    private Segment segment;
    private Long counterId;

    @Parameterized.Parameter
    public Operator operator;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {Operator.IN},
                {Operator.IN_ALIAS},
                {Operator.NOT_IN},
                {Operator.NOT_IN_ALIAS}
        });
    }

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
    public void maximumAllowedOperandsTest() {
        segment.setExpression(
                user.onFilterSteps().getMultiOperandFilter(DIMENSION_NAME, operator, MAXIMUM_OPERANDS));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectSuccess(counterId, segment);
    }

    @Test
    public void moreThanMaximumAllowedOperandsTest() {
        segment.setExpression(
                user.onFilterSteps().getMultiOperandFilter(DIMENSION_NAME, operator, MAXIMUM_OPERANDS + 1));

        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ReportError.TOO_MANY_VALUES_IN_FILTER,
                counterId, segment);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
