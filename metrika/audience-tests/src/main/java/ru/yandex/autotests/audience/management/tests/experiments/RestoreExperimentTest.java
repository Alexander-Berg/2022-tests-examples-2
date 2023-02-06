package ru.yandex.autotests.audience.management.tests.experiments;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 *
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.EXPERIMENTS})
@Title("Experiment: восстановление эксперимента")
@RunWith(Parameterized.class)
public class RestoreExperimentTest {
    private final User owner = USER_DELEGATOR;

    private ExperimentAB experiment;
    private Long experimentId;
    private UserSteps user;

    @Parameter
    public User userParam;

    @Parameter(1)
    public String userDescription;

    @Parameterized.Parameters(name = "пользователь {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                getSuperUser().toArray(),
                getUserWithPermEdit().toArray(),
                getOwner().toArray()
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
        experiment = user.onExperimentSteps().createExperiment(getSimpleExperiment(USER_DELEGATOR), ulogin(owner));
        experimentId = experiment.getExperimentId();
        user.onExperimentSteps().deleteExperiment(experimentId, ulogin(owner));

        user.onExperimentSteps().restoreExperiment(experimentId, ulogin(owner));
    }

    @Test
    public void checkExperimentIsInList() {
        List<ExperimentAB> experiments = user.onExperimentSteps().getExperiments(ulogin(owner));

        assertThat("восстановленный эксперимент присутствует в списке", experiments,
                hasBeanEquivalent(ExperimentAB.class, experiment));
    }

    @After
    public void tearDown() {
        user.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId, ulogin(owner));
    }
}
