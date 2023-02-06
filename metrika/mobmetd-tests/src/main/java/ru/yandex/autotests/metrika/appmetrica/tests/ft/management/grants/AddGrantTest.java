package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationPermission;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.parameters.IncludeAgencyAppParameter.INCLUDE_AGENCY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.formatIsoDtf;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by graev on 15/01/2017.
 */
@Features(Requirements.Feature.Management.Application.GRANTS)
@Stories({
        Requirements.Story.Application.Grants.ADD,
        Requirements.Story.Application.Grants.LIST,
        Requirements.Story.Application.Grants.INFO,
})
@Title("Добавление доступа")
@RunWith(Parameterized.class)
public final class AddGrantTest {

    public static final User MANAGER = Users.SIMPLE_USER;

    public static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final UserSteps granteeSteps = UserSteps.onTesting(GRANTEE);

    private static final TestData.GrantCreator GRANTS = forUser(GRANTEE);

    @Parameterized.Parameter()
    public GrantWrapper grantToAdd;

    @Parameterized.Parameter(value = 1)
    public MobmetGrantE expectedGrant;

    @Parameterized.Parameter(value = 2)
    public ApplicationPermission expectedPermission;

    private Long appId;

    private MobmetGrantE addedGrant;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(GRANTS.grant(VIEW)))
                .add(param(GRANTS.grant(EDIT)))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        addedGrant = managerSteps.onGrantSteps().createGrant(appId, grantToAdd);
    }

    @Test
    public void checkGrantInfo() {
        assertThat("добавленный грант эквивалентен ожидаемому",
                addedGrant, equivalentTo(expectedGrant));
    }

    @Test
    public void checkActualGrantInfo() {
        final MobmetGrantE grant = managerSteps.onGrantSteps().getGrant(appId, GRANTEE.get(LOGIN));
        assertThat("добавленный грант эквивалентен актуальному",
                grant, equivalentTo(addedGrant));
    }

    @Test
    public void checkGrantInList() {
        final List<MobmetGrantE> grantList = managerSteps.onGrantSteps().getGrantList(appId);
        assertThat("список грантов приложения содержит грант, эквивалентный ожидаемому",
                grantList, hasItem(equivalentTo(addedGrant)));
    }

    @Test
    public void checkGrantedAppPermissions() {
        final Application application = granteeSteps.onApplicationSteps().getApplication(appId);
        assertThat("приложение содержит добавленную информацию о доступе",
                application.getPermission(), equalTo(expectedPermission));
    }

    @Test
    public void checkGrantedAppInList() {
        final List<Application> applicationList = granteeSteps.onApplicationSteps().getApplications();
        assertThat("приложение присутствует в стандартном списке приложений",
                applicationList, hasItem(hasProperty("id", equalTo(appId))));
    }

    @Test
    public void grantedAppInFullList() {
        final List<Application> applicationList = granteeSteps.onApplicationSteps().getApplications(INCLUDE_AGENCY);
        assertThat("приложение присутствует в расширенном списке приложений",
                applicationList, hasItem(hasProperty("id", equalTo(appId))));
    }

    @Test
    public void checkApplicationHasPermissionDate() {
        final Application actual = granteeSteps.onApplicationSteps().getApplicationFromList(appId);

        assertThat("приложение из списка имеет ожидаемую дату выдачи доступа",
                formatIsoDtf(actual.getPermissionDate()), startsWith(actual.getCreateDate()));
    }

    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE grant) {
        return toArray(new GrantWrapper(grant), grant, appPermission(grant));
    }

    private static ApplicationPermission appPermission(MobmetGrantE grant) {
        return ImmutableMap.<GrantType, ApplicationPermission>builder()
                .put(GrantType.VIEW, ApplicationPermission.VIEW)
                .put(GrantType.EDIT, ApplicationPermission.EDIT)
                .build().get(grant.getPerm());
    }

}

