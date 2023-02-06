package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos on 19.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка разрыва связи с метками при переносе счетчика")
public class MovedCounterIsNotAvailableTest {
    private static final User OWNER_USER = SIMPLE_USER;
    private static final User RECIPIENT = Users.SIMPLE_USER2;

    private UserSteps userOwner = new UserSteps().withUser(OWNER_USER);
    private UserSteps userNewOwner = new UserSteps().withUser(RECIPIENT);
    private CounterFull counter;
    private Label label;
    private long labelId;
    private long counterId;

    @Before
    public void setup() {
        counter = getDefaultCounter();
        label = getDefaultLabel();
        counterId = userOwner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();

        userOwner.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);

        userOwner.onManagementSteps().onCountersSteps().moveCounter(counterId, RECIPIENT.get(LOGIN));
    }

    @Test
    @Title("Счетчик не привязан к метке после перемещения")
    public void movedCounterShouldNotBeInCountersList() {
        List<CounterFull> counters = userOwner.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);
        assertThat("счетчик отсутствует в списке счетчиков по метке", counters, not(hasItem(beanEquivalent(counter))));
    }

    @After
    public void tearDown() {
        userNewOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
