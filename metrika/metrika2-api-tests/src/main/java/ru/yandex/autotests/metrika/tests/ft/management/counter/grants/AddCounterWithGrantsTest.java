package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.Field;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Date;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с правами доступа")
@RunWith(Parameterized.class)
public class AddCounterWithGrantsTest {
    private UserSteps user;
    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;
    private GrantE resultGrant;

    @Parameter(0)
    public String granteeLogin;

    @Parameter(1)
    public GrantE expectedGrant;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[]{"IVKSoft", new GrantE()
                        .withUserLogin("IVKSoft")
                        .withPerm(GrantType.VIEW)
                        .withComment("Доступ к сайту президента России")},
                new Object[]{USER_GRANTEE.get(LOGIN).toUpperCase(), new GrantE()
                        .withUserLogin(USER_GRANTEE.get(LOGIN))
                        .withPerm(GrantType.VIEW)
                        .withComment("Доступ к сайту президента России")});
    }


    @Before
    public void before() {
        user = new UserSteps();
        counter = new CounterFull()
                .withName(ManagementTestData.getCounterName())
                .withSite(ManagementTestData.getCounterSite())
                .withGrants(
                        asList(new GrantE()
                                .withUserLogin(granteeLogin)
                                .withPerm(GrantType.VIEW)
                                .withComment("Доступ к сайту президента России")
                        )
                );

        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, Field.GRANTS);
        counterId = addedCounter.getId();

        resultGrant = addedCounter.getGrants().get(0);
    }

    @Test
    @Title("Права доступа: логин пользователя")
    public void grantsUserLoginTest() {
        String result = resultGrant.getUserLogin();
        String expected = expectedGrant.getUserLogin();

        assertThat("Логин пользователя совпадает с заданным", expected, equalTo(result));
    }

    @Test
    @Title("Права доступа: уровень доступа")
    public void grantsPermTest() {
        String result = resultGrant.getPerm().toString();
        String expected = expectedGrant.getPerm().toString();

        assertThat("Уровень доступа совпадает с заданным", expected, equalTo(result));
    }

    @Test
    @Title("Права доступа: дата предоставления доступа")
    public void grantsCreatedAtTest() {
        Date result = resultGrant.getCreatedAt();

        assertThat("Дата предоставления доступа должна быть не null", result, not(nullValue()));
    }

    @Test
    @Title("Права доступа: комментарий")
    public void grantsCommentTest() {
        String result = resultGrant.getComment();
        String expected = expectedGrant.getComment();

        assertThat("Комментарий совпадает с заданным", expected, equalTo(result));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
