package ru.yandex.autotests.audience.management.tests.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.segmentab.ExperimentAB;
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
import static org.hamcrest.Matchers.not;
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
@Title("Доступ: удаление доступа на эксперимент")
public class DeleteExperimentGrantTest {
    private static final UserSteps userOwner = UserSteps.withUser(SIMPLE_USER);
    private final UserSteps userGrantee = UserSteps.withUser(USER_GRANTEE);

    private Long experimentId;
    private Grant grant;

    @Before
    public void init() {
        experimentId = userOwner.onExperimentSteps().createExperiment(TestData.getSimpleExperiment(SIMPLE_USER)).getExperimentId();
        grant = getGrant();
        userOwner.onExperimentGrantsSteps().createGrant(experimentId, grant);

    }

    @Test
    public void checkDeleteGrant() {
        userOwner.onExperimentGrantsSteps().deleteGrant(experimentId, grant.getUserLogin());
        List<Grant> grants = userOwner.onExperimentGrantsSteps().getGrants(experimentId);

        assertThat("доступ отсутствует в списке", grants,
                not(hasBeanEquivalent(Grant.class, grant)));
    }

    @Test
    public void checkDeleteGrantInSegmentList() {
        userOwner.onExperimentGrantsSteps().deleteGrant(experimentId, grant.getUserLogin());
        List<ExperimentAB> experiments = userGrantee.onExperimentSteps().getExperiments();

        assertThat("эксперимент отсутствует в списке", experiments,
                not(hasItem(having(on(ExperimentAB.class).getExperimentId(), equalTo(experimentId)))));
    }

    @Test
    public void checkDeleteGrantSelf() {
        userGrantee.onExperimentGrantsSteps().deleteGrant(experimentId, "");
        List<ExperimentAB> experiments = userGrantee.onExperimentSteps().getExperiments();

        assertThat("эксперимент отсутствует в списке", experiments,
                not(hasItem(having(on(ExperimentAB.class).getExperimentId(), equalTo(experimentId)))));
    }

    @After
    public void cleanUp() {
        userOwner.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId);
    }
}
