package ru.yandex.autotests.audience.management.tests.experiments;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 *
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.EXPERIMENTS})
@Title("Experiment: удаление эксперимента")
@RunWith(Parameterized.class)
public class DeleteExperimentTest {
    private final User owner = USER_DELEGATOR;

    private Long experimentId;
    private UserSteps userSteps;

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
        userSteps = UserSteps.withUser(userParam);
        experimentId = userSteps.onExperimentSteps().createExperiment(getSimpleExperiment(owner), ulogin(owner)).getExperimentId();

        userSteps.onExperimentSteps().deleteExperiment(experimentId, ulogin(owner));
    }

    @Test
    public void checkDeletedExperimentInList() {
        List<ExperimentAB> experiments = userSteps.onExperimentSteps().getExperiments(ulogin(owner));

        assertThat("удаленный эксперимент отсутствует в списке", experiments,
                not(hasItem(having(on(ExperimentAB.class).getExperimentId(), equalTo(experimentId)))));
    }
}
