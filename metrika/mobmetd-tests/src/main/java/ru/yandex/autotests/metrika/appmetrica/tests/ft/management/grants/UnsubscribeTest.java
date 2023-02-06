package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
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
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.GRANT_NOT_FOUND;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Проверить, что можно удалить свой гостевой доступ
 * <p>
 * Created by graev on 20/12/2016.
 */
@Features(Requirements.Feature.Management.Application.GRANTS)
@Stories({
        Requirements.Story.Application.Grants.UNSUBSCRIBE
})
@Title("Удаление себя из гостевого доступа приложения")
@RunWith(Parameterized.class)
public final class UnsubscribeTest {
    private static final User OWNER = Users.SIMPLE_USER;

    private static final User GRANTEE = Users.SIMPLE_USER_2;

    private static final UserSteps ownerSteps = UserSteps.onTesting(OWNER);

    private static final UserSteps granteeSteps = UserSteps.onTesting(GRANTEE);

    private static final GrantCreator GRANTS = forUser(GRANTEE);

    private Long appId;

    @Parameterized.Parameter
    public GrantWrapper grant;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(GRANTS.grant(VIEW)),
                param(GRANTS.grant(EDIT)),
                param(GRANTS.agencyViewGrant()),
                param(GRANTS.agencyEditGrant())
        );
    }

    @Before
    public void setup() {
        final Application application = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();
        ownerSteps.onGrantSteps().createGrant(appId, grant);
        granteeSteps.onGrantSteps().deleteGrant(appId, null); // remove itself
    }

    @Test
    public void checkGrantNotFound() {
        ownerSteps.onGrantSteps().getGrantAndExpectError(appId, GRANTEE.get(LOGIN), GRANT_NOT_FOUND);
    }

    @Test
    public void checkGrantNotInList() {
        final List<MobmetGrantE> grants = ownerSteps.onGrantSteps().getGrantList(appId);
        assertThat("удаленный грант отсутствует в списке грантов", grants,
                not(hasItem(hasProperty("user_login", equalTo(GRANTEE.get(LOGIN))))));
    }

    @After
    public void tearDown() {
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, GRANTEE.get(LOGIN));
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(MobmetGrantE grant) {
        return toArray(new GrantWrapper(grant));
    }
}
