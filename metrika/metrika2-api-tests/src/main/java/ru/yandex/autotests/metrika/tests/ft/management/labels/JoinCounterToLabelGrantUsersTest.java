package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by vananos on 13.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@RunWith(Parameterized.class)
@Title("Проверка возможности привязки метки к счетчику пользователями с правами EDIT и VIEW")
public class JoinCounterToLabelGrantUsersTest {
    private static final User GRANTEE_USER = USER_GRANTEE;

    private static UserSteps userOwner = new UserSteps();

    @Parameter
    public GrantType grantType;

    private UserSteps userGtantee = new UserSteps().withUser(GRANTEE_USER);
    private long labelId;
    private long counterId;

    @Parameters(name = "Права: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray(VIEW),
                toArray(EDIT));
    }

    @Before
    public void setup() {
        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();

        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId,
                new GrantE()
                        .withUserLogin(GRANTEE_USER.get(LOGIN))
                        .withPerm(grantType));
    }

    @Test
    public void joinCounterToLabelTest() {
        userGtantee.onManagementSteps().onLabelsSteps()
                .joinCounterToLabelAndExpectError(ACCESS_DENIED, counterId, labelId);

        List<CounterFull> countersByLabel = userOwner.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);

        assertThat("привязанный счетчик присутствует в списке счетчиков метки", countersByLabel,
                not(hasItem(having(on(CounterFull.class).getId(), equalTo(counterId)))));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
