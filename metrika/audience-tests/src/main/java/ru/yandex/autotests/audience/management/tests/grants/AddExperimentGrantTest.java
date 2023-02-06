package ru.yandex.autotests.audience.management.tests.grants;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.audience.management.tests.TestData.getGrant;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Доступ: выдача доступа на эксперимент")
public class AddExperimentGrantTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);
    private static final User GRANTEE = USER_GRANTEE;

    private final UserSteps userGrantee = UserSteps.withUser(GRANTEE);

    private static Long experimentId;
    private static Grant grant;

    @BeforeClass
    public static void setup() {
        ExperimentAB experiment = user.onExperimentSteps().createExperiment(TestData.getSimpleExperiment(SIMPLE_USER));
        experimentId = experiment.getExperimentId();
        grant = getGrant(GRANTEE);

        user.onExperimentGrantsSteps().createGrant(experimentId, grant);
    }

    @Test
    public void checkAddGrant() {
        List<Grant> grants = user.onExperimentGrantsSteps().getGrants(experimentId);

        assertThat("доступ присутствует в списке", grants,
                hasBeanEquivalent(Grant.class, grant));
    }

    @Test
    public void checkGranteeSegmentList() {
        List<ExperimentAB> experiments = userGrantee.onExperimentSteps().getExperiments();

        assertThat("эксперимент присутствует в списке у пользователя, которому выдали права", experiments,
                hasItem(having(on(ExperimentAB.class).getExperimentId(), equalTo(experimentId))));
    }

    @AfterClass
    public static void tearDown() {
        user.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId);
    }
}
