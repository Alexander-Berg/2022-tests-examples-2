package ru.yandex.autotests.audience.management.tests.experiments;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.management.tests.TestData.getSimpleExperiment;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

/**
 *
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: управление экспериментом (негативные тесты)")
@RunWith(Parameterized.class)
public class ExperimentActionsPermissionNegativeTest {
    private final User owner = USER_DELEGATOR;
    private final UserSteps userOwner = UserSteps.withUser(owner);

    private UserSteps user;
    private Long experimentId;

    @Parameter
    public String description;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на просмотр", USER_WITH_PERM_VIEW),
                toArray("с ролью менеджер", MANAGER),
                toArray("без прав", SIMPLE_USER)
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
        experimentId = userOwner.onExperimentSteps().createExperiment(getSimpleExperiment(owner)).getExperimentId();
    }

    @Test
    public void checkTryCreateExperiment() {
        user.onExperimentSteps().createExperimentAndExpectError(ACCESS_DENIED, getSimpleExperiment(owner), ulogin(owner));
    }

    @Test
    public void checkTryEditExperiment() {
        user.onExperimentSteps().editExperimentAndExpectError(experimentId, ACCESS_DENIED, getSimpleExperiment(owner), ulogin(owner));
    }

    @Test
    public void checkTryDeleteExperiment() {
        user.onExperimentSteps().deleteExperimentAndExpectError(ACCESS_DENIED, experimentId, ulogin(owner));
    }

    @Test
    public void checkTryRestoreExperiment() {
        userOwner.onExperimentSteps().deleteExperiment(experimentId);
        user.onExperimentSteps().restoreExperimentAndExpectError(ACCESS_DENIED, experimentId, ulogin(owner));
    }

    @After
    public void tearDown() {
        userOwner.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId);
    }
}
