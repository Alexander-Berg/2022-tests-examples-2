package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.matchers.CounterMatchers.beanEquivalentIgnoringFeatures;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 29.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка изменения данных счетчика")
@Issues({
        @Issue("METR-8834"),
        @Issue("METR-17097")
})
@RunWith(Parameterized.class)
public class EditCounterTest {

    private UserSteps user;
    private Long counterId;
    private CounterFull changedCounter;
    private CounterFull editedCounter;

    @Parameter(0)
    public User userParam;

    @Parameter(1)
    public CounterFullObjectWrapper counterWrapper;

    @Parameter(2)
    public EditAction<CounterFull> counterChangeAction;

    @Parameters(name = "{1}; {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createEditParam(getCounterWithBasicParameters(), getChangeName()),
                createEditParam(getCounterWithBasicParameters(), getChangeSite()),
                createEditParam(getCounterWithClickMap(1L), getChangeClickMap(0L)),
                createEditParam(getCounterWithClickMap(0L), getChangeClickMap(1L)),
                createEditParam(USER_WITH_ONE_PHONE, getCounterWithOnePhone(1L, 1L), getChangeEnableMonitoring(0L)),
                createEditParam(USER_WITH_ONE_PHONE, getCounterWithOnePhone(1L, 1L), getChangeEnableSms(0L)),
                createEditParam(USER_WITH_ONE_PHONE, getCounterWithOnePhone(1L, 1L), getChangePhone(null, null)),
                // +78120344573
                createEditParam(USER_WITH_TWO_PHONES, getCounterWithOneOfTwoPhones(1L, 1L), getChangePhone(asList("+7000*****73"), asList(119356347L))),
                createEditParam(USER_WITH_TWO_PHONES, getCounterWithTwoPhones(1L, 1L), getChangePhone(asList("+7000*****73"), asList(119356347L))),
                createEditParam(getCounterWithCurrency(978L), getChangeCurrency(980L)),
                createEditParam(getCounterWithCurrency(980L), getChangeCurrency(643L)),
                createEditParam(getCounterWithCurrency(978L), getChangeTimeZone("Europe/London")),
                createEditParam(getDefaultCounter(), getChangeWebVisorUrls(2000)),
                createEditParam(getDefaultCounter(), getChangeEcommerceEnabled(1L)),
                createEditParam(getCounterWithAlternativeCdn(0L), getChangeAlternativeCdn(1L)),
                createEditParam(getCounterWithAlternativeCdn(1L), getChangeAlternativeCdn(0L)),
                createEditParam(getCounterWithEcommerce(1L),getChangeEcommerceEnabled(0L)),
                createEditParam(getCounterWithEcommerceObject("dataLayer1"), getChangeEcommerceObject("dataLayer2")),
                createEditParam(getCounterWithEcommerceObject(1), getChangeEcommerceObject(200)),
                createEditParam(getDefaultCounter(), getAddOperation()),
                createEditParam(getDefaultCounterWithPublicStatPermission(), getRemovePublicStatPermission()),
                createEditParam(getDefaultCounter(), getAddPublicStatPermission()),
                createEditParam(getCounterWithGoals(getActionGoal(), getURLGoal()), getChangeReverseGoalsOrder()),
                createEditParam(getCounterWithGoals(getStepGoal(), getURLGoal()), getChangeReverseGoalsOrder()),
                createEditParam(getCounterWithGoals(getStepGoal()), getRemoveGoalStep()),
                createEditParam(getDefaultCounter(), getAddUrlGoal()),
                createEditParam(getDefaultCounter(), getAddActionGoal()),
                createEditParam(getDefaultCounter(), getAddNumberGoal()),
                createEditParam(getDefaultCounter(), getAddStepGoal()),
                createEditParam(getDefaultCounter(), getAddMaximumGoals()),
                createEditParam(getDefaultCounter(), getAddMaximumFilters()),
                createEditParam(getCounterWithGoals(getStepGoal(), getNumberGoal()), getDeleteGoal()),
                createEditParam(getCounterWithGoals(getActionGoal(), getStepGoal()), getDeleteAllGoals()),
                createEditParam(getDefaultCounter(), getAddOperation()),
                createEditParam(getDefaultCounter(), getAddMaximumOperations()),
                createEditParam(getDefaultCounter(), getChangeSiteWithPath()),
                createEditParam(getDefaultCounter(), getChangeSiteWithUnderscore()),
                createEditParam(getDefaultCounterWithMirror(), getChangeSiteWithPath()),
                createEditParam(getDefaultCounterWithMirror(), getChangeSiteWithUnderscore()),
                createEditParam(getDefaultCounter(), getChangeMirrorsWithPath()),
                createEditParam(getDefaultCounter(), getChangeMirrorsWithUnderscore()),
                createEditParam(getDefaultCounter(), getChangeFavoriteState(1L)),
                createEditParam(SIMPLE_USER2_EMAIL, getDefaultCounter(), getChangeFavoriteState(1L)),
                createEditParam(USER_WITH_PHONE_LOGIN, getDefaultCounter(), getChangeFavoriteState(1L)),
                createEditParam(USER_WITH_PHONE_ONLY_LOGIN, getDefaultCounter(), getChangeFavoriteState(1L)),
                createEditParam(SIMPLE_USER_PDD, getDefaultCounter(), getChangeFavoriteState(1L)),
                createEditParam(getDefaultCounter(), getEnableOfflineConversionExtendedThreshold()),
                createEditParam(getDefaultCounter(), getEnableOfflineCallsExtendedThreshold()),
                createEditParam(getCounterWithOfflineConversionExtendedThresholdEnabled(), getDisableOfflineConversionExtendedThreshold()),
                createEditParam(getCounterWithOfflineCallsExtendedThresholdEnabled(), getDisableOfflineCallsExtendedThreshold()),
                createEditParam(getCounterWithGdprAgreementAccepted(false), getAcceptGdprAgreement()),
                createEditParam(getCounterWithGdprAgreementAccepted(true), getRejectGdprAgreement()),
                createEditParam(getDefaultCounter(), getEnablePublishers()),
                createEditParam(getDefaultCounter(), getSetPublishersSchema()),
                createEditParam(getCounterWithPublisherEnabled(), getDisablePublishers())
        );
    }

    @Before
    public void before() {
        user = new UserSteps().withUser(userParam);
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counterWrapper.get()).getId();
        changedCounter = counterChangeAction.edit(counterWrapper.getClone());
        editedCounter = user.onManagementSteps().onCountersSteps().editCounter(counterId, changedCounter, all());
    }

    @Test
    public void checkEditedCounter() {
        assertThat("отредактированный счетчик должен быть эквивалентен измененному счетчику", editedCounter,
                beanEquivalentIgnoringFeatures(changedCounter));
    }

    @Test
    public void checkCounterInfo() {
        CounterFull counterInfo = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, all());

        assertThat("информация об отредактированном счетчике должна быть эквивалентна измененному счетчику",
                counterInfo, beanEquivalentIgnoringFeatures(changedCounter));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
