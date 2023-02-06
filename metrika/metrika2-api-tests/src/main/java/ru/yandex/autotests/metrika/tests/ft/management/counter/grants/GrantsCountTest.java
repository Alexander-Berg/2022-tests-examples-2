package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.lang.Long.valueOf;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 08.09.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GRANTS)
@Title("Проверка соответствия поля grants_cnt количеству выданных прав")
@Issue("METR-17891")
public class GrantsCountTest {

    private UserSteps user;

    private final static User OWNER = SIMPLE_USER;
    private final static String FIELD = "grants_cnt";

    private CounterFull counter;
    private Long counterId;

    @Before
    public void setup() {
        user = new UserSteps().withUser(OWNER);

        counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        counterId = counter.getId();
    }

    private AvailableCountersParameters getParameters() {
        return new AvailableCountersParameters().withField(FIELD);
    }

    @Test
    public void checkNoGrants() {
        CounterBrief counterInList = user.onManagementSteps().onCountersSteps()
                .getCounterFromList(counterId, getParameters());

        assertThat("количество прав у счетчика без доступов равно 0", counterInList.getGrantsCnt(),
                equalTo(0L));
    }

    @Test
    public void checkOneGrant() {
        user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(SIMPLE_USER2));

        CounterBrief counterInList = user.onManagementSteps().onCountersSteps()
                .getCounterFromList(counterId, getParameters());

        assertThat("количество прав у счетчика с доступом равно 1", counterInList.getGrantsCnt(), equalTo(1L));
    }

    @Test
    public void checkMultipleGrants() {
        List<GrantE> grants = asList(getGrant(SIMPLE_USER2),
                getGrant(SIMPLE_USER_PDD),
                getGrant(USER_WITH_PHONE_LOGIN));

        Long expectedCount = valueOf(grants.size());

        user.onManagementSteps().onGrantsSteps().setGrantsAndExpectSuccess(counterId, grants);

        CounterBrief counterInList = user.onManagementSteps().onCountersSteps()
                .getCounterFromList(counterId, getParameters());

        assertThat(format("количество прав у счетчика с доступом равно %s", expectedCount),
                counterInList.getGrantsCnt(), equalTo(expectedCount));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
