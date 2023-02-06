package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos on 01.08.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка неизменности комментария при выдаче нового доступа на счетчик")
@Issue("METR-12753")
public class GrantCommentsTest {
    private static final String GRANTEE_USER_LOGIN = SIMPLE_USER2.get(LOGIN);
    private static final String FIRST_COMMENT = "Комментарий №1";
    private static final String SECOND_COMMENT = "Комментарий №2, отличается от первого";

    private UserSteps user = new UserSteps();
    private long firstCounterId;
    private long secondCounterId;
    private GrantE expectedGrant = new GrantE()
            .withUserLogin(GRANTEE_USER_LOGIN)
            .withPerm(GrantType.EDIT)
            .withComment(FIRST_COMMENT);

    @Before
    public void setup() {
        firstCounterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
        secondCounterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(firstCounterId, expectedGrant);
        user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(secondCounterId,
                new GrantE()
                        .withUserLogin(GRANTEE_USER_LOGIN)
                        .withPerm(GrantType.EDIT)
                        .withComment(SECOND_COMMENT));
    }

    @Test
    @Title("Права не должны быть изменены")
    public void grantShouldNotBeChanged() {
        GrantE actualGrant = user.onManagementSteps().onGrantsSteps().getGrantAndExpectSuccess(firstCounterId,
                GRANTEE_USER_LOGIN);

        assertThat("права доступа совпадают с ожидаемыми", actualGrant, beanEquivalent(expectedGrant));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(firstCounterId);
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(secondCounterId);
    }
}
