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
@Title("Проверка невозможности открепления метки от счетчика пользователями с правами EDIT и VIEW")
@RunWith(Parameterized.class)
public class CancelJoinCounterToLabelGrantUserTest {
    private static final User GRANTEE_USER = USER_GRANTEE;

    private UserSteps userOwner = new UserSteps().withDefaultAccuracy();
    private UserSteps userGrantee = new UserSteps().withUser(GRANTEE_USER);
    private Long labelId;
    private Long counterId;

    @Parameter
    public GrantType grantType;

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

        userOwner.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);
        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId,
                new GrantE()
                        .withUserLogin(GRANTEE_USER.get(LOGIN))
                        .withPerm(grantType));
    }

    @Test
    public void cancelJoinCounterToLabelTest() {
        userGrantee.onManagementSteps().onLabelsSteps()
                .cancelJoinCounterToLabelAndExpectError(ACCESS_DENIED, counterId, labelId);

        List<CounterFull> countersByLabel = userOwner.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);
        assertThat("счетчик должен быть в списке счетчиков метки",
                countersByLabel, hasItem(having(on(CounterFull.class).getId(), equalTo(counterId))));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
