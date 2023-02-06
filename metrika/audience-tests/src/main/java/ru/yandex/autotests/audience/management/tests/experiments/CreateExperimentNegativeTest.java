package ru.yandex.autotests.audience.management.tests.experiments;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
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
@Title("Experiment: создание эксперимента (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateExperimentNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    @Parameter
    public String description;

    @Parameter(1)
    public ExperimentAB request;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
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
                        EXPERIMENT_TOO_FEW_SEGMENTS),
                toArray("сегменты не по порядку",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("50", "100"),getSegmentAB("0", "50"))),
                        EXPERIMENT_WRONG_SEGMENT_BOUNDARIES),
                toArray("пустой сегмент",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "0"),getSegmentAB("0", "100"))),
                        EXPERIMENT_EMPTY_SEGMENT),
                toArray("перекрытие сегментов",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "51"),getSegmentAB("50", "100"))),
                        EXPERIMENT_WRONG_SEGMENT_BOUNDARIES),
                toArray("разрыв между сегментами",
                        getSimpleExperiment(SIMPLE_USER).withSegments(Arrays.asList(getSegmentAB("0", "50"),getSegmentAB("51", "100"))),
                        EXPERIMENT_WRONG_SEGMENT_BOUNDARIES),
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

    @Test
    public void checkTryCreateExperiment() {
        user.onExperimentSteps().createExperimentAndExpectError(error, request);
    }
}
