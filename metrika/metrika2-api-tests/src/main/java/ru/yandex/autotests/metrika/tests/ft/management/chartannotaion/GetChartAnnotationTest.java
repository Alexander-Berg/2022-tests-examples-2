package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: получение информации о примечании")
public class GetChartAnnotationTest {

    private static final MetrikaChartAnnotation ANNOTATION = getDefaultAnnotation();

    private static final UserSteps user = new UserSteps();

    private Long counterId;
    private Long annotationId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        annotationId = user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, ANNOTATION)
                .getId();
    }

    @Test
    public void test() {
        MetrikaChartAnnotation receivedAnnotation = user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotation(counterId, annotationId);

        assertThat("полученное примечание совпадает с ожидаемым", receivedAnnotation, beanEquivalent(ANNOTATION));
    }

    @After
    public void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
