package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants.agency;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper.wrap;

/**
 * Created by graev on 01/12/2016.
 */
@Features(Requirements.Feature.Management.Application.Grants.AGENCY)
@Stories({
        Requirements.Story.Application.Grants.Agency.EDIT
})
@Title("Редактирование агентского доступа")
@RunWith(Parameterized.class)
public final class EditAgencyGrantTest {

    private static final User MANAGER = Users.SIMPLE_USER;

    private static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final GrantCreator GRANTS = forUser(GRANTEE);

    private final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    @Parameterized.Parameter()
    public GrantWrapper grantToAdd;

    @Parameterized.Parameter(value = 1)
    public EditAction<MobmetGrantE, MobmetGrantE> editAction;

    private MobmetGrantE editedGrant;
    private MobmetGrantE expectedGrant;
    private long appId;

    @Parameters(name = "{0}. {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(GRANTS.defaultAgencyGrant(), changePartner()))
                .add(param(GRANTS.defaultAgencyGrant(), changeEvents()))
                .add(param(GRANTS.defaultAgencyGrant(), changeGrantType()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = managerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        MobmetGrantE addedGrant = managerSteps.onGrantSteps().createGrant(appId, grantToAdd);
        expectedGrant = editAction.edit(addedGrant);
        editedGrant = managerSteps.onGrantSteps().editGrant(appId, wrap(editAction.getUpdate(addedGrant)));
    }

    @Test
    public void checkGrantInfo() {
        assertThat("отредактированный грант эквивалентен ожидаемому",
                editedGrant, equivalentTo(expectedGrant));
    }

    @Test
    public void checkActualGrantInfo() {
        final MobmetGrantE grant = managerSteps.onGrantSteps().getGrant(appId, GRANTEE.get(LOGIN));
        assertThat("актуальный грант эквивалентен ожидаемому",
                grant, equalTo(expectedGrant));
    }


    @After
    public void teardown() {
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        managerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE grant, EditAction<MobmetGrantE, MobmetGrantE> action) {
        return toArray(new GrantWrapper(grant), action);
    }
}
