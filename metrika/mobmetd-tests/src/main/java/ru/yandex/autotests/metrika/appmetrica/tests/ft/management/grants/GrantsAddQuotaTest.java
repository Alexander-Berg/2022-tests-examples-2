package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;


import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.GrantsParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.GRANTS_QUOTA_EXCEEDED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.Management.Application.GRANTS)
@Stories({
        Requirements.Story.Application.Grants.ADD,
        Requirements.Story.Application.Grants.QUOTA
})
@Title("Проверка квот на добавление доступов")
@RunWith(Parameterized.class)
public class GrantsAddQuotaTest {

    private static final int MAX_ATTEMPTS = 3;

    private static final User MANAGER = Users.SIMPLE_USER;

    private static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final TestData.GrantCreator GRANTS = forUser(GRANTEE);

    @Parameterized.Parameter()
    public GrantWrapper grantToCreate;

    private Long appId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(GRANTS.grant(VIEW)))
                .add(param(GRANTS.grant(EDIT)))
                .add(param(GRANTS.getAgencyEditGrantToMultiplePartners()))
                .add(param(GRANTS.getAgencyViewGrantToMultiplePartnersAndEvents()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        for (int i = 0; i < MAX_ATTEMPTS; ++i) {
            managerSteps.onGrantSteps().createGrant(appId, grantToCreate);
            managerSteps.onGrantSteps().deleteGrant(appId, GRANTEE.get(LOGIN));
        }
    }

    @Test
    public void add() {
        managerSteps.onGrantSteps().createGrantAndExpectError(appId, grantToCreate, GRANTS_QUOTA_EXCEEDED);
    }

    @Test
    public void addWithQuotaIgnore() {
        managerSteps.onGrantSteps().createGrant(appId, grantToCreate, new GrantsParameters().quotaIgnore());
    }

    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE grant) {
        return toArray(new GrantWrapper(grant));
    }
}
