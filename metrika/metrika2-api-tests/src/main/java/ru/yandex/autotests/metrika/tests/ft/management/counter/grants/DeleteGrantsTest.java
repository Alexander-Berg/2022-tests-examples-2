package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 05.03.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GRANTS)
@Title("Проверка отзыва прав доступа к счетчику")
@Issues({
        @Issue("METRIKASUPP-4621"),
        @Issue("METRIKASUPP-4953"),
        @Issue("METRIKASUPP-5450")
})
@RunWith(Parameterized.class)
public class DeleteGrantsTest {

    private UserSteps userOwner;
    private UserSteps userGrantee;

    private final static User OWNER = SIMPLE_USER;
    private Long counterId;
    private GrantE grant;

    @Parameter
    public User grantee;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {SIMPLE_USER2},
                {SIMPLE_USER_PDD},
                {USER_WITH_PHONE_LOGIN}
        });
    }

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(OWNER);
        userGrantee = new UserSteps().withUser(grantee);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        grant = getGrant(grantee);
        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, grant);
    }

    @Test
    public void ownerShouldRemoveGrant() {
        userOwner.onManagementSteps().onGrantsSteps()
                .deleteGrantAndExpectSuccess(counterId, grantee.get(LOGIN));

        assertThat("удаленное разрешение отсутствует в списке разрешений",
                userOwner.onManagementSteps().onGrantsSteps().getGrantsAndExpectSuccess(counterId),
                not(hasItem(beanEquivalent(grant))));
    }

    @Test
    public void granteeShouldRemoveOwnGrant() {
        userGrantee.onManagementSteps().onGrantsSteps()
                .deleteGrantAndExpectSuccess(counterId, grantee.get(LOGIN));

        assertThat("удаленное разрешение отсутствует в списке разрешений",
                userOwner.onManagementSteps().onGrantsSteps().getGrantsAndExpectSuccess(counterId),
                not(hasItem(beanEquivalent(grant))));
    }

    @Test
    public void granteeShouldRemoveOwnGrantWithoutLogin() {
        userGrantee.onManagementSteps().onGrantsSteps()
                .deleteGrantAndExpectSuccess(counterId, null);

        assertThat("удаленное разрешение отсутствует в списке разрешений",
                userOwner.onManagementSteps().onGrantsSteps().getGrantsAndExpectSuccess(counterId),
                not(hasItem(beanEquivalent(grant))));
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
