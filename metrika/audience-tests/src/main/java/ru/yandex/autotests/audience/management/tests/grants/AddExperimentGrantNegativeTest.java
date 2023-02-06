package ru.yandex.autotests.audience.management.tests.grants;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.GRANT_HAS_ALREADY_CREATED;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_EMPTY;
import static ru.yandex.autotests.audience.errors.ManagementError.USER_NOT_FOUND;
import static ru.yandex.autotests.audience.management.tests.TestData.createGrantNegativeParam;
import static ru.yandex.autotests.audience.management.tests.TestData.getDmpSegment;
import static ru.yandex.autotests.audience.management.tests.TestData.getGrant;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Доступ: выдача доступа на эксперимент (негативные тесты)")
@RunWith(Parameterized.class)
public class AddExperimentGrantNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private static Long experimentId;

    @Parameter()
    public String description;

    @Parameter(1)
    public Grant grant;

    @Parameter(2)
    public Long experimentIdParam;

    @Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {3}")
    public static Collection<Object[]> createParameters() {
        experimentId = user.onExperimentSteps().createExperiment(TestData.getSimpleExperiment(SIMPLE_USER)).getExperimentId();
        user.onExperimentGrantsSteps().createGrant(experimentId, getGrant(USER_FOR_LOOKALIKE));

        return ImmutableList.of(
                createGrantNegativeParam("несуществующий эксперимент", RandomUtils.getString(15), experimentId,
                        USER_NOT_FOUND),
                createGrantNegativeParam("пустой userLogin", StringUtils.EMPTY, experimentId, NOT_EMPTY),
                createGrantNegativeParam("в отправляемом json отсуствует поле userLogin", null,
                        experimentId, NOT_EMPTY),
                createGrantNegativeParam("повторная выдача доступа", USER_FOR_LOOKALIKE.toString(), experimentId,
                        GRANT_HAS_ALREADY_CREATED)
        );
    }

    @Test
    public void checkTryAddGrant() {
        user.onExperimentGrantsSteps().createGrantAndExpectError(error, experimentIdParam, grant);
    }

    @AfterClass
    public static void cleanUp() {
        user.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId);
    }
}
