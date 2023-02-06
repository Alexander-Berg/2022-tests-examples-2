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
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GRANTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 13.04.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GRANTS)
@Title("Проверка выдачи прав доступа к счетчику")
@Issues({
        @Issue("METRIKASUPP-4953"),
        @Issue("METRIKASUPP-5450")
})
@RunWith(Parameterized.class)
public class AddGrantsTest {

    private UserSteps user;

    private final static User OWNER = SIMPLE_USER;

    private Long counterId;

    @Parameter(0)
    public User grantee;

    @Parameter(1)
    public GrantE expectedGrant;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                createAddGrantParam(SIMPLE_USER2),
                createAddGrantParam(SIMPLE_USER_PDD),
                createAddGrantParam(USER_WITH_PHONE_LOGIN,
                        getGrant(USER_WITH_PHONE_LOGIN).withUserLogin("at-metrika-8"))
        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(OWNER);

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, expectedGrant);
    }

    @Test
    public void checkGrants() {
        List<GrantE> grants = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, GRANTS).getGrants();

        assertThat("выданные права доступа присутствуют в списке прав доступа счетчика", grants,
                hasItem(beanEquivalent(expectedGrant)));
    }

    @Test
    public void ownerShouldManipulatePublicGrant() {

        user.onManagementSteps().onGrantsSteps()
                .setGrantAndExpectSuccess(counterId, new GrantE().withPerm(GrantType.PUBLIC_STAT));

        assertThat("у счетчика есть публичный доступ",
                user.onManagementSteps().onGrantsSteps().getGrantsAndExpectSuccess(counterId),
                hasItem(beanEquivalent(new GrantE().withPerm(GrantType.PUBLIC_STAT))));

        user.onManagementSteps().onGrantsSteps()
                .deletePublicGrantAndExpectSuccess(counterId);

        assertThat("к счетчику нет публичного доступа",
                user.onManagementSteps().onGrantsSteps().getGrantsAndExpectSuccess(counterId),
                not(hasItem(beanEquivalent(new GrantE().withPerm(GrantType.PUBLIC_STAT)))));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
