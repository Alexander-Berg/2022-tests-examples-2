package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants.agency;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.GRANT_NOT_FOUND;
import static ru.yandex.autotests.metrika.appmetrica.parameters.IncludeAgencyAppParameter.INCLUDE_AGENCY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper.wrap;

/**
 * Created by graev on 01/12/2016.
 */
@Features(Requirements.Feature.Management.Application.Grants.AGENCY)
@Stories({
        Requirements.Story.Application.Grants.Agency.DELETE
})
@Title("Удаление агентского доступа")
public final class DeleteAgencyGrantTest {

    public static final User MANAGER = Users.SIMPLE_USER;

    public static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final UserSteps granteeSteps = UserSteps.onTesting(GRANTEE);

    private static final GrantCreator GRANTS = forUser(GRANTEE);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        managerSteps.onGrantSteps().createGrant(appId, wrap(GRANTS.defaultAgencyGrant()));
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
    }

    @Test
    public void checkGrantNotFound() {
        managerSteps.onGrantSteps().getGrantAndExpectError(appId, GRANTEE.get(LOGIN), GRANT_NOT_FOUND);
    }

    @Test
    public void checkAppNotFound() {
        granteeSteps.onApplicationSteps().getApplicationAndExpectError(FORBIDDEN, appId);
    }

    @Test
    public void checkGrantIsNotInList() {
        final List<MobmetGrantE> grants = managerSteps.onGrantSteps().getGrantList(appId);
        assertThat("после удаление гранта, грант отсутствует в списке",
                grants, not(hasItem(hasProperty("user_login", equalTo(GRANTEE.get(LOGIN))))));
    }

    @Test
    public void checkAppIsNotInList() {
        final List<Application> apps = granteeSteps.onApplicationSteps().getApplications(INCLUDE_AGENCY);
        assertThat("после удаления гранта приложение не отображается в списке",
                apps, not(hasItem(hasProperty("id", equalTo(appId)))));
    }

    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

}
