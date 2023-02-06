package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.negative;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getDefaultAnnotation;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getNegativeAnnotationParams;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: изменение примечания (негативные)")
@RunWith(Parameterized.class)
public class EditChartAnnotationNegativeTest {

    private static final UserSteps user = new UserSteps();

    private static Long counterId;

    private Long annotationId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return getNegativeAnnotationParams();
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public MetrikaChartAnnotation annotation;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        annotationId = user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();
    }

    @Test
    public void test() {
        user.onManagementSteps().onChartAnnotationSteps()
                .editAnnotationAndExpectError(error, counterId, annotationId, annotation);
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
