package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getDefaultAnnotation;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: удаление примечания")
public class DeleteChartAnnotationTest {

    private static final UserSteps user = new UserSteps();

    private Long counterId;
    private Long annotationId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        annotationId = user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();
    }

    @Test
    public void test() {
        user.onManagementSteps().onChartAnnotationSteps()
                .deleteAnnotation(counterId, annotationId);
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
