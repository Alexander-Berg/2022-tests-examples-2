package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
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
@Title("Примечания на графиках: изменение примечания")
@RunWith(Parameterized.class)
public class EditChartAnnotationTest {

    private static final UserSteps user = new UserSteps();

    private static Long counterId;

    private Long annotationId;

    @Parameterized.Parameters(name = "Действие: {1}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(getDefaultAnnotation(), getChangeTitleAction()),
                toArray(getDefaultAnnotation(), getChangeDateAction()),
                toArray(getDefaultAnnotation(), getChangeGroupAction()),
                toArray(getAnnotationWithTime(), getChangeTimeAction()),
                toArray(getAnnotationWithMessage(), getChangeMessageAction())
        );
    }

    @Parameterized.Parameter
    public MetrikaChartAnnotation annotation;

    @Parameterized.Parameter(1)
    public EditAction<MetrikaChartAnnotation> editAction;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        annotationId = user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, annotation)
                .getId();
    }

    @Test
    public void test() {
        annotation = editAction.edit(annotation);

        MetrikaChartAnnotation editedAnnotation = user.onManagementSteps().onChartAnnotationSteps()
                .editAnnotation(counterId, annotationId, annotation);

        assertThat("измененное примечание совпадает с ожидаемым", editedAnnotation, beanEquivalent(annotation));
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
