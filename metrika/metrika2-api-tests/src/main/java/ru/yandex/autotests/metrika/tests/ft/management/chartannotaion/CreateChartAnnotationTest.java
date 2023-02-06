package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: создание примечания")
@RunWith(Parameterized.class)
public class CreateChartAnnotationTest {

    private static final UserSteps user = new UserSteps();

    private static Long counterId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray("Базовое примечание", getDefaultAnnotation()),
                toArray("Альтернативное примечание", getAlternativeAnnotation()),
                toArray("Примечание с временем", getAnnotationWithTime()),
                toArray("Примечание с описанием", getAnnotationWithMessage())
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public MetrikaChartAnnotation annotation;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void test() {
        MetrikaChartAnnotation createdAnnotation = user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, annotation);

        assertThat("созданное примечание совпадает с ожидаемым", createdAnnotation, beanEquivalent(annotation));
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
