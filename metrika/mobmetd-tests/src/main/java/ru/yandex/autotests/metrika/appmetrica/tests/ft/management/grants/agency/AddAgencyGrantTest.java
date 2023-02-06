package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants.agency;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
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
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.formatIsoDtf;

/**
 * Создаем агентский доступ для приложения и проверяем что система ведет себя ожидаемо
 * <p>
 * Created by graev on 30/11/2016.
 */
@Features(Requirements.Feature.Management.Application.Grants.AGENCY)
@Stories({
        Requirements.Story.Application.Grants.Agency.ADD,
        Requirements.Story.Application.Grants.Agency.LIST,
        Requirements.Story.Application.Grants.Agency.INFO,
})
@Title("Добавление агентского доступа")
@RunWith(Parameterized.class)
public final class AddAgencyGrantTest {

    public static final User MANAGER = Users.SIMPLE_USER;

    public static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final UserSteps granteeSteps = UserSteps.onTesting(GRANTEE);

    private static final GrantCreator GRANTS = forUser(GRANTEE);

    @Parameter()
    public GrantWrapper grantToAdd;

    @Parameter(value = 1)
    public MobmetGrantE expectedGrant;

    @Parameter(value = 2)
    public ApplicationPermission expectedPermission;

    private Long appId;

    private MobmetGrantE addedGrant;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(GRANTS.getAgencyEditGrantToMultiplePartners()))
                .add(param(GRANTS.getAgencyViewGrantToMultiplePartnersAndEvents()))
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
        assertThat("агентское приложение содержит добавленную информацию о доступе",
                application.getPermission(), equalTo(expectedPermission));
    }

    @Test
    public void checkGrantedAppIsNotInList() {
        final List<Application> applicationList = granteeSteps.onApplicationSteps().getApplications();
        assertThat("агентское приложение отсутствует в стандартном списке приложений",
                applicationList, not(hasItem(hasProperty("id", equalTo(appId)))));
    }

    @Test
    public void grantedAppInFullList() {
        final List<Application> applicationList = granteeSteps.onApplicationSteps().getApplications(INCLUDE_AGENCY);
        assertThat("агентское приложение содержится в расширенном списке приложений",
                applicationList, hasItem(hasProperty("id", equalTo(appId))));
    }

    @Test
    public void checkAgencyApplicationHasPermissionDate() {
        final Application actual = granteeSteps.onApplicationSteps().getApplicationFromList(appId, INCLUDE_AGENCY);

        assertThat("агентское приложение из списка имеет ожидаемую дату выдачи доступа",
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
                .put(GrantType.AGENCY_VIEW, ApplicationPermission.AGENCY_VIEW)
                .put(GrantType.AGENCY_EDIT, ApplicationPermission.AGENCY_EDIT)
                .build().get(grant.getPerm());
    }

}
