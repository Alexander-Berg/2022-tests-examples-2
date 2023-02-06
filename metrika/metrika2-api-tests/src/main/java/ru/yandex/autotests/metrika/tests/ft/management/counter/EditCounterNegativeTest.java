package ru.yandex.autotests.metrika.tests.ft.management.counter;

import java.util.Collection;

import com.google.common.collect.Lists;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Issues;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.metrika.errors.ManagementError.ECOMMERCE_OBJECT_SIZE;
import static ru.yandex.autotests.metrika.errors.ManagementError.EMPTY_GOAL_CONDITION;
import static ru.yandex.autotests.metrika.errors.ManagementError.FILTERS_LIMIT;
import static ru.yandex.autotests.metrika.errors.ManagementError.GOALS_LIMIT;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_CURRENCY_CODE;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_SITE_ONLY_DOMAIN;
import static ru.yandex.autotests.metrika.errors.ManagementError.OPERATIONS_LIMIT;
import static ru.yandex.autotests.metrika.errors.ManagementError.WEBVISOR_URLS_LIST_TOO_LARGE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createEditNegativeParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getAddMoreThanMaximumFilters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getAddMoreThanMaximumGoals;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getAddMoreThanMaximumOperations;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getChangeCurrency;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getChangeEcommerceObject;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getChangeMirrors2;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getChangeSite2;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getChangeWebVisorUrls;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithCurrency;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithEcommerceObject;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithGoals;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSetGoalNullConditions;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getURLGoal;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка изменения данных счетчика (негативные тесты)")
@Issues({
        @Issue("METR-17097")
})
@RunWith(Parameterized.class)
public class EditCounterNegativeTest {
    private static UserSteps user;

    private Long counterId;
    private CounterFull changedCounter;

    @Parameterized.Parameter(0)
    public CounterFullObjectWrapper counterWrapper;

    @Parameterized.Parameter(1)
    public EditAction<CounterFull> counterChangeAction;

    @Parameterized.Parameter(2)
    public IExpectedError expectedError;

    @Parameterized.Parameters(name = "{1}; {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createEditNegativeParam(getCounterWithCurrency(978L), getChangeCurrency(644L),
                        INVALID_CURRENCY_CODE),
                createEditNegativeParam(getCounterWithCurrency(978L), getChangeCurrency(1L),
                        INVALID_CURRENCY_CODE),
                createEditNegativeParam(getDefaultCounter(), getChangeWebVisorUrls(2001),
                        WEBVISOR_URLS_LIST_TOO_LARGE),
                createEditNegativeParam(getCounterWithEcommerceObject("notDataLayerObject"),
                        getChangeEcommerceObject(201),
                        ECOMMERCE_OBJECT_SIZE),
                createEditNegativeParam(getDefaultCounter(), getAddMoreThanMaximumFilters(),
                        FILTERS_LIMIT),
                createEditNegativeParam(getDefaultCounter(), getAddMoreThanMaximumGoals(),
                        GOALS_LIMIT),
                createEditNegativeParam(getDefaultCounter(), getAddMoreThanMaximumOperations(),
                        OPERATIONS_LIMIT),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeSite2("!@#$.ru"),
                        INVALID_SITE_ONLY_DOMAIN),
                // "xn--,-stbcq.xn--80aswg" == toASCII("лпк,.сайт")
                createEditNegativeParam(getDefaultCounter(),
                        getChangeSite2("xn--,-stbcq.xn--80aswg"),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeSite2("лпк,.сайт"),
                        INVALID_SITE_ONLY_DOMAIN),
                // "xn--et8h.ga" == toASCII("📅.ga")
                createEditNegativeParam(getDefaultCounter(),
                        getChangeSite2("\uD83D\uDCC5.ga"),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeSite2("xn--et8h.ga"),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeMirrors2(Lists.newArrayList("!@#$.ru")),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeMirrors2(Lists.newArrayList("xn--,-stbcq.xn--80aswg")),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeMirrors2(Lists.newArrayList("лпк,.сайт")),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeMirrors2(Lists.newArrayList("\uD83D\uDCC5.ga")),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        getChangeMirrors2(Lists.newArrayList("xn--et8h.ga")),
                        INVALID_SITE_ONLY_DOMAIN),
                createEditNegativeParam(getDefaultCounter(),
                        EditAction.create("null parameter", c -> null),
                        MAY_NOT_BE_NULL),
                createEditNegativeParam(getCounterWithGoals(getURLGoal()),
                        getSetGoalNullConditions(),
                        EMPTY_GOAL_CONDITION)
        );
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(SIMPLE_USER);
    }

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counterWrapper.get()).getId();
    }

    @Test
    public void checkTryEditCounter() {
        changedCounter = counterChangeAction.edit(counterWrapper.get());
        user.onManagementSteps().onCountersSteps().editCounterAndExpectError(expectedError, counterId, changedCounter);
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
