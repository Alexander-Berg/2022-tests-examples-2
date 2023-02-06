package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER_WITHOUT_MONEY_1;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GRANTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createAddGrantParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GRANTS)
@Title("Проверка выдачи прав доступа к счетчику c фичей РСЯ")
@RunWith(Parameterized.class)
public class AddGrantsWithPartnerAccessTest {

    private UserSteps user;

    private static final User OWNER = METRIKA_TEST_COUNTERS;

    private static final Long COUNTER_ID = Counters.PARTNER_TEST_3.getId();

    @Parameter(0)
    public User grantee;

    @Parameter(1)
    public GrantE expectedGrant;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createAddGrantParam(SIMPLE_USER_WITHOUT_MONEY_1, getGrant(SIMPLE_USER_WITHOUT_MONEY_1).withPartnerDataAccess(true).withPerm(EDIT)),
                createAddGrantParam(SIMPLE_USER_WITHOUT_MONEY_1, getGrant(SIMPLE_USER_WITHOUT_MONEY_1).withPartnerDataAccess(true).withPerm(VIEW)),
                createAddGrantParam(SIMPLE_USER_WITHOUT_MONEY_1, getGrant(SIMPLE_USER_WITHOUT_MONEY_1).withPartnerDataAccess(false).withPerm(VIEW)));
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(OWNER);
        user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(COUNTER_ID, expectedGrant,
                ignoreQuota(true));
    }

    @Test
    public void checkGrants() {
        List<GrantE> grants = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(COUNTER_ID, GRANTS).getGrants();

        assertThat("выданные права доступа присутствуют в списке прав доступа счетчика", grants,
                hasItem(beanEquivalent(expectedGrant)));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(COUNTER_ID, expectedGrant.getUserLogin());
    }
}
