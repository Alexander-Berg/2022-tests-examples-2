package ru.yandex.autotests.audience.management.tests.experiments;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static java.util.Collections.emptyList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 *
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.EXPERIMENTS})
@Title("Experiment: редактирование эксперимента (негативные тесты)")
@RunWith(Parameterized.class)
public class EditExperimentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private static Long experimentId;

    @Parameter
    public String description;

    @Parameter(1)
    public ExperimentAB request;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>of(
                toArray("пустое имя эксперимента",
                        getSimpleExperiment(SIMPLE_USER).withName(StringUtils.EMPTY),
                        INCORRECT_STRING_LENGTH),
                toArray("слишком длинное имя эксперимента",
                        getSimpleExperiment(SIMPLE_USER).withName(EXPERIMENT_TOO_LONG_NAME),
                        INCORRECT_STRING_LENGTH),
                toArray("отсутствует параметр name",
                        getSimpleExperiment(SIMPLE_USER).withName(null),
                        NOT_NULL),
                toArray("пустой список счетчиков",
                        getSimpleExperiment(SIMPLE_USER).withCounterIds(emptyList()),
                        EXPERIMENT_TOO_FEW_COUNTERS),
                toArray("отсутствует список счетчиков",
                        getSimpleExperiment(SIMPLE_USER).withCounterIds(null),
                        EXPERIMENT_TOO_FEW_COUNTERS),
                toArray("слишком длинный список счетчиков",
                        getSimpleExperiment(SIMPLE_USER).withCounterIds(Arrays.asList(1L,2L,3L,4L,5L,6L)),
                        EXPERIMENT_TOO_MANY_COUNTERS),
                toArray("отсутствует список сегментов",
                        getSimpleExperiment(SIMPLE_USER).withSegments(null),
                        EXPERIMENT_SEGMENTS_NOT_EMPTY),
                toArray("пустой список сегментов",
                        getSimpleExperiment(SIMPLE_USER).withSegments(emptyList()),
                        EXPERIMENT_SEGMENTS_NOT_EMPTY),
                toArray("один сегмент",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "100"))),
                        EXPERIMENT_INCORRECT_SEGMENTS_COUNT),
                toArray("количество сегментов отличается от указанного при создании",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "100"),getSegmentAB("0", "100"),getSegmentAB("0", "100"))),
                        EXPERIMENT_INCORRECT_SEGMENTS_COUNT),
                toArray("пустое имя сегмента",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "50").withName(""),getSegmentAB("50", "100"))),
                        INCORRECT_STRING_LENGTH),
                toArray("отсутствует имя сегмента",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "50").withName(null),getSegmentAB("50", "100"))),
                        NOT_NULL),
                toArray("слишком длинное имя сегмента",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "50").withName(SEGMENT_TOO_LONG_NAME),getSegmentAB("50", "100"))),
                        INCORRECT_STRING_LENGTH)
                );
    }

    @BeforeClass
    public static void init() {
        experimentId = user.onExperimentSteps().createExperiment(getSimpleExperiment(SIMPLE_USER)).getExperimentId();
    }

    @Test
    public void checkTryEditExperiment() {
        user.onExperimentSteps().editExperimentAndExpectError(experimentId, error, request);
    }

    @AfterClass
    public static void cleanUp() {
        user.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId);
    }

}
