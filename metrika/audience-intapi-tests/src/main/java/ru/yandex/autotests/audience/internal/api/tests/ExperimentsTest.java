package ru.yandex.autotests.audience.internal.api.tests;

import org.junit.Test;
import ru.yandex.audience.internal.InternalV1ExperimentGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentSegmentGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentSegmentsGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentsGETSchema;
import ru.yandex.autotests.audience.internal.api.parameters.ExperimentParameters;
import ru.yandex.autotests.audience.internal.api.parameters.ExperimentSegmentParameters;
import ru.yandex.autotests.audience.internal.api.parameters.ExperimentSegmentsParameters;
import ru.yandex.autotests.audience.internal.api.parameters.ExperimentsParameters;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.CRYPTA;
import static ru.yandex.autotests.audience.internal.api.errors.IntapiError.INVALID_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.COUNTER_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.DELETED_EXPERIMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.EXPERIMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.NON_EXISTENT_EXPERIMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.SEGMENT_A_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.SEGMENT_B_ID;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(CRYPTA)
@Title("Проверка ручек связанные с экспериментами")
public class ExperimentsTest {
    public final UserSteps user = new UserSteps();

    @Test
    @Title("Тест ручки /internal/v1/experiment")
    public void geExperimentTest() {
        InternalV1ExperimentGETSchema users = user.onExperimentsSteps().getExperiment(ExperimentParameters.id(EXPERIMENT_ID));

        assertThat("существует эксперимент с заданным ID", users.getExperiment(), notNullValue());
    }

    @Test
    @Title("Тест ручки /internal/v1/experiment_segment")
    public void geExperimentSegmentTest() {
        InternalV1ExperimentSegmentGETSchema users = user.onExperimentsSteps().getExperimentSegment(ExperimentSegmentParameters.id(SEGMENT_A_ID));

        assertThat("существует сегмент эксперимента с заданным ID", users.getExperimentSegment(), notNullValue());
    }

    @Test
    @Title("Тест ручки /internal/v1/experiment_segments")
    public void getExperimentSegmentListTest() {
        Integer[] experimentSegmentsIds = {SEGMENT_A_ID, SEGMENT_B_ID};
        InternalV1ExperimentSegmentsGETSchema users = user.onExperimentsSteps().getExperimentSegments(ExperimentSegmentsParameters.ids(experimentSegmentsIds));

        assertThat("существуют сегменты эксперимента с заданными списком ID", users.getExperimentSegmentList(), iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Тест ручки /internal/v1/experiments")
    public void getExperimentListTest() {
        InternalV1ExperimentsGETSchema users = user.onExperimentsSteps().getExperiments(ExperimentsParameters.counterId(COUNTER_ID));

        assertThat("существуют эксперименты у заданного счетчика", users.getExperiments(), iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Тест ручки /internal/v1/experiment. Пытаться получить несуществующий эксперимент")
    public void tryToGetExperimentThatDoesNotExistTest() {
        user.onExperimentsSteps()
                .getExperimentAndExpectError(INVALID_ID, ExperimentParameters.id(NON_EXISTENT_EXPERIMENT_ID));
    }

    @Test
    @Title("Тест ручки /internal/v1/experiment. Пытаться получить эксперимент который удален")
    public void tryToGetExperimentThatDeletedTest() {
        user.onExperimentsSteps()
                .getExperimentAndExpectError(INVALID_ID, ExperimentParameters.id(DELETED_EXPERIMENT_ID));
    }
}
