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
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 29.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка отвязки метки от счетчика пользователям с различными ролями:  владелец, представитель, менеджер, саппорт")
@RunWith(Parameterized.class)
public class CancelJoinCounterToLabelTest {
    private static final User OWNER_ACCOUNT = USER_DELEGATOR;
    private static final User DELEGATE_ACCOUNT = USER_DELEGATE_PERMANENT;

    private static UserSteps userOwner = new UserSteps().withUser(OWNER_ACCOUNT);

    private UserSteps userWithPermission;
    private Long labelId;
    private Long counterId;

    @Parameter(0)
    public String userRole;

    @Parameter(1)
    public User userAccount;

    @Parameters(name = "Роль: {0}, Пользователь: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Владелец", OWNER_ACCOUNT),
                toArray("Представитель", DELEGATE_ACCOUNT),
                toArray("Менеджер", MANAGER),
                toArray("Саппорт", SUPPORT));
    }

    @Before
    public void setup() {
        userWithPermission = new UserSteps().withUser(userAccount);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();

        userOwner.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);
    }

    @Test
    public void cancelJoinCounterToLabelTest() {
        userWithPermission.onManagementSteps().onLabelsSteps()
                .cancelJoinCounterToLabelAndExpectSuccess(counterId, labelId);

        List<CounterFull> countersByLabel = userOwner.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);
        assertThat("отвязанный счетчик должен отсутствовать в списке счетчиков метки",
                countersByLabel, not(hasItem(having(on(CounterFull.class).getId(), equalTo(counterId)))));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
