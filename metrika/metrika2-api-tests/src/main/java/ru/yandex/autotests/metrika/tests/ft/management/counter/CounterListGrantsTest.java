package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GRANTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.CounterPermission.VIEW;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Права на счётчики из списка")
public class CounterListGrantsTest {

    private UserSteps user;
    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    private static final User OWNER = SIMPLE_USER;
    private static final User GRANTEE = Users.SIMPLE_USER2;

    @Before
    public void before() {
        user = new UserSteps().withUser(OWNER);
        counter = getDefaultCounter();
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, GRANTS);
        counterId = addedCounter.getId();

        GrantE grant = new GrantE()
                .withUserLogin(GRANTEE.get(LOGIN))
                .withPerm(GrantType.VIEW)
                .withComment("");
        counter.getGrants().add(grant);
        user.onManagementSteps().onCountersSteps().editCounter(counterId, counter, GRANTS,
                ignoreQuota(true));
    }

    @Test
    @Title("Метка: есть права на счётчик")
    public void joinCounterToLabelPermTest() {
        List<CounterBrief> availableCounters =
                user.withUser(GRANTEE)
                        .onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess();
        CounterBrief expectedCounter = new CounterBrief()
                .withId(counterId)
                .withName(counter.getName())
                .withSite(counter.getSite())
                .withPermission(VIEW);

        assertThat("Привязанный счетчик присутствует в списке счетчиков", availableCounters,
                hasItem(beanEquivalent(expectedCounter)));
    }

    @Test
    @Title("Метка: нет прав на счётчик")
    public void joinCounterToLabelNoPermTest() {
        counter.setGrants(new ArrayList<GrantE>());
        user.withUser(OWNER)
                .onManagementSteps().onCountersSteps().editCounter(counterId, counter, GRANTS);

        List<CounterBrief> availableCounters =
                user.withUser(GRANTEE).onManagementSteps().onCountersSteps()
                        .getAvailableCountersAndExpectSuccess(new AvailableCountersParameters());
        CounterBrief expectedCounter = new CounterBrief()
                .withId(counterId);

        assertThat("Привязанный счетчик отсутствует в списке счетчиков метки", availableCounters,
                not(hasItem(beanEquivalent(expectedCounter))));
    }

    @After
    public void after() {
        user.withUser(OWNER).onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
