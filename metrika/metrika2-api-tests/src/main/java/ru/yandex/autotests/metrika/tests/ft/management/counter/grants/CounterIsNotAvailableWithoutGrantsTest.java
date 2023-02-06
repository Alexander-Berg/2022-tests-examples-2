package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

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
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by vananos on 19.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Разрыв связи счетчика с метками после отзыва прав у пользователя")
@RunWith(Parameterized.class)
public class CounterIsNotAvailableWithoutGrantsTest {
    private static final User GRANTEE_USER = SIMPLE_USER;

    private UserSteps userOwner = new UserSteps();
    private UserSteps userGrantee = new UserSteps().withUser(GRANTEE_USER);

    private CounterFull counter;
    private Label label;
    private long labelId;
    private long counterId;

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
        counter = getDefaultCounter();
        label = getDefaultLabel();
        counterId = userOwner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();
        labelId = userGrantee.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();

        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId,
                new GrantE().withPerm(grantType).withUserLogin(GRANTEE_USER.get(LOGIN)));
        userGrantee.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);

        userOwner.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(counterId, GRANTEE_USER.get(LOGIN));
    }

    @Test
    @Title("Счетчик не привязан к метке")
    public void counterShouldNotBeInCountersList() {
        List<CounterFull> counters = userGrantee.onManagementSteps()
                .onLabelsSteps().getCountersByLabelAndExpectSuccess(labelId);
        assertThat("созданный счетчик отсутствует в списке счетчиков", counters, not(hasItem(beanEquivalent(counter))));
    }

    @Test
    @Title("Метка не привязана к счетчику")
    public void labelShouldNotBeInCounterInfo() {
        List<Label> labels = userOwner.onManagementSteps().onCountersSteps().getCounterInfo(counterId).getLabels();
        assertThat("метка отсутствует в списке привязанных меток", labels, not(hasItem(beanDiffer(label))));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userGrantee.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
