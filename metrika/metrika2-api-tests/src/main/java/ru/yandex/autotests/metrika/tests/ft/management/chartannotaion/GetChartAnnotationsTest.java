package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getAlternativeAnnotation;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.getDefaultAnnotation;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: получение списка примечаний")
public class GetChartAnnotationsTest {

    private static final List<MetrikaChartAnnotation> ANNOTATIONS = of(
            getDefaultAnnotation(),
            getAlternativeAnnotation()
    );

    private static final UserSteps user = new UserSteps();

    private Long counterId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        ANNOTATIONS.forEach(annotation -> user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, annotation)
        );
    }

    @Test
    public void test() {
        List<MetrikaChartAnnotation> receivedAnnotations = user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotations(counterId);

        assertThat("полученный список примечаний совпадает с ожидаемым",
                receivedAnnotations,
                containsInAnyOrder(ANNOTATIONS.stream()
                        .map(BeanDifferMatcher::beanEquivalent)
                        .collect(toList())
                )
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
