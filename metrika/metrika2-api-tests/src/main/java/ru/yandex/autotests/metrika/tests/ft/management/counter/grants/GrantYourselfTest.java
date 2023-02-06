package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GRANTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

/**
 * Created by konkov on 12.12.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка назначения прав доступа счетчика самому себе")
@Issue("METR-14210")
public class GrantYourselfTest {
    private UserSteps user;
    private UserSteps userCounterGrantee;

    private final static User OWNER = SIMPLE_USER;
    private final static User GRANTEE = Users.SUPPORT;
    private CounterFull counter;
    private Long counterId;

    @Before
    public void setup() {
        user = new UserSteps().withUser(OWNER);
        userCounterGrantee = new UserSteps().withUser(GRANTEE);

        counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());

        counterId = counter.getId();
    }

    private GrantE getExpectedGrant() {
        return new GrantE()
                .withUserLogin(GRANTEE.get(LOGIN))
                .withPerm(EDIT)
                .withComment("Доступ самому себе");
    }

    @Test
    @Title("Права доступа: выдать доступ самому себе")
    public void grantYourselfTest() {
        CounterFull editedCounter = counter.withGrants(asList(getExpectedGrant()));

        userCounterGrantee.onManagementSteps().onCountersSteps().editCounter(counterId, editedCounter);

        List<GrantE> editedGrants = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, GRANTS).getGrants();

        assertThat("права доступа совпадают с заданными", editedGrants,
                hasItem(beanEquivalent(getExpectedGrant())));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
