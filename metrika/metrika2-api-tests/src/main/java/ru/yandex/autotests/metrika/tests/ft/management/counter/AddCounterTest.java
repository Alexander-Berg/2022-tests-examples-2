package ru.yandex.autotests.metrika.tests.ft.management.counter;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beans.BeanHelper.copyProperties;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_ONE_PHONE;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_TWO_PHONES;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.matchers.CounterMatchers.beanEquivalentIgnoringFeatures;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка добавления счетчика")
@Issues({
        @Issue("METR-16371"),
        @Issue("METR-14714"),
        @Issue("METR-8834"),
        @Issue("METR-17097")
})
@RunWith(Parameterized.class)
public class AddCounterTest {
    public static final long IRKUTSK_TIMEZONE_OFFSET = 480L;

    private UserSteps user;
    private Long counterId;
    private CounterFull addedCounter;

    @Parameter(0)
    public User userParam;

    @Parameter(1)
    public CounterFullObjectWrapper counterWrapperToAdd;

    @Parameter(2)
    public CounterFullObjectWrapper counterWrapperExpected;

    @Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>of(
                createAddParam(getCounterWithBasicParameters()),
                createAddParam(getCounterWithGoals(getURLGoal())),
                createAddParam(getCounterWithGoals(getNumberGoal())),
                createAddParam(getCounterWithGoals(getStepGoal())),
                createAddParam(getCounterWithGoalsWithDefaultPrice(getActionGoalWithDefaultPrice(199.99))),
                createAddParam(getCounterWithGoals(getActionGoal())),
                createAddParam(getCounterWithGoals(getURLGoal(), getNumberGoal(), getActionGoal())),
                createAddParam(getCounterWithClickMap(1L)),
                createAddParam(getCounterWithClickMap(0L)),
                createAddParam(USER_WITH_ONE_PHONE, getCounterWithOnePhone(1L, 1L)),
                createAddParam(USER_WITH_TWO_PHONES, getCounterWithTwoPhones(1L, 1L)),
                createAddParam(getCounterWithCurrency(840L)),
                createAddParam(getCounterWithCurrency(933L)),
                createAddParam(getCounterWithCurrency(null), getCounterWithCurrency(643L)),
                createAddParam(getCounterWithTimeZone(null), getCounterWithTimeZone("Europe/Moscow")),
                createAddParam(getCounterWithWebVisorUrls(2000)),
                createAddParam(getCounterWithAlternativeCdn(0L)),
                createAddParam(getCounterWithAlternativeCdn(1L)),
                createAddParam(getCounterWithEcommerce(1L)),
                createAddParam(getCounterWithEcommerce(0L)),
                createAddParam(getCounterWithEcommerceObject("notDataLayer")),
                createAddParam(getCounterWithEcommerceObject(EMPTY), getCounterWithEcommerceObject("dataLayer")),
                createAddParam(getCounterWithEcommerceObject(200)),
                createAddParam(getCounterWithOperation()),
                createAddParam(getCounterWithGoals(getMaximumGoals())),
                createAddParam(getCounterWithFilters(getMaximumFilters())),
                createAddParam(getCounterWithOperations(getMaximumOperations())),
                createAddParam(getCounterWithTimeZone("Asia/Irkutsk").withTimeZoneOffset(IRKUTSK_TIMEZONE_OFFSET)), //Не дефолтная таймзона
                createAddParam(getCounterWithPathInSite()),
                createAddParam(getCounterWithUnderscoreInSite()),
                createAddParam(getCounterWithPathInMirrors()),
                createAddParam(getCounterWithUnderscoreInMirrors()),
                createAddParam(getCounterWithOfflineConversionExtendedThresholdEnabled()),
                createAddParam(getCounterWithOfflineCallsExtendedThresholdEnabled()),
                createAddParam(getDefaultCounter(), getCounterWithGdprAgreementAccepted(false)), // false by default
                createAddParam(getCounterWithGdprAgreementAccepted(false)),
                createAddParam(getCounterWithGdprAgreementAccepted(true)),
                createAddParam(getCounterWithPublisherEnabled()),
                createAddParam(getCounterWithPublisherEnabledAndSchema()),
                createAddParam(getCounterWithSourceAndExistsNameAndSite(CounterSource.SPRAV)),
                createAddParam(getCounterWithSourceAndExistsNameAndSite(CounterSource.DZEN)),
                createAddParam(getDefaultCounter().withFeatures(Arrays.asList(Feature.VACUUM))),
                createAddParam(getDefaultCounter().withAutogoalsEnabled(false)),
                createAddParam(getDefaultCounter().withAutogoalsEnabled(true)),
                createAddParam(getDefaultCounter().withFilterRobots(2L))
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counterWrapperToAdd.get(), all());

        counterId = addedCounter.getId();
    }

    @Test
    public void checkAddedCounter() {
        assertThat("добавленный счетчик должен быть эквивалентен добавляемому", addedCounter,
                beanEquivalentIgnoringFeatures(counterWrapperExpected.get()));
    }

    @Test
    public void checkCounterInfo() {
        CounterFull actualCounter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, all());

        assertThat("информация о счетчике должна быть эквивалентна добавляемому счетчику", actualCounter,
                beanEquivalentIgnoringFeatures(counterWrapperExpected.get()));
    }

    @Test
    public void counterShouldBeInCountersList() {
        List<CounterBrief> counters = user.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess();

        CounterBrief expectedCounterBrief = new CounterBrief();
        copyProperties(counterWrapperExpected.get(), expectedCounterBrief);

        assertThat("список должен содержать добавленный счетчик", counters,
                hasItem(beanEquivalentIgnoringFeatures(expectedCounterBrief)));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
