package ru.yandex.autotests.metrika.tests.ft.management.counter;

import com.google.common.collect.Lists;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_EMPTY_TOKEN;
import static ru.yandex.autotests.metrika.errors.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка добавления счетчика (негативные тесты)")
@Issues({
        @Issue("METR-17097")
})
@RunWith(Parameterized.class)
public class AddCounterNegativeTest {

    private static UserSteps user;

    @Parameter(0)
    public User owner;

    @Parameter(1)
    public CounterFullObjectWrapper counterWrapperToAdd;

    @Parameter(2)
    public IExpectedError expectedError;

    @Parameters(name = "{1}: {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createAddNegativeParam(null, MAY_NOT_BE_NULL),
                createAddNegativeParam(getCounterWithEmptySite(), INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getCounterWithWrongTimezone(), WRONG_TIME_ZONE),
                createAddNegativeParam(USER_WITH_EMPTY_TOKEN, getCounterWithBasicParameters(),
                        UNAUTHORIZED),
                createAddNegativeParam(getCounterWithCurrency(644L),
                        INVALID_CURRENCY_CODE),
                createAddNegativeParam(getCounterWithCurrency(1L),
                        INVALID_CURRENCY_CODE),
                createAddNegativeParam(getCounterWithWebVisorUrls(2001),
                        WEBVISOR_URLS_LIST_TOO_LARGE),
                createAddNegativeParam(getCounterWithEcommerceObject(201),
                        ECOMMERCE_OBJECT_SIZE),
                createAddNegativeParam(getCounterWithGoals(getMoreThanMaximumGoals()),
                        GOALS_LIMIT),
                createAddNegativeParam(getCounterWithFilters(getMoreThamMaximumFilters()),
                        FILTERS_LIMIT),
                createAddNegativeParam(getCounterWithOperations(getMoreThanMaximumOperations()),
                        OPERATIONS_LIMIT),
                createAddNegativeParam(getDefaultCounter().withSite2(new CounterMirrorE().withSite("!@#$.ru")),
                        INVALID_SITE_ONLY_DOMAIN),
                // "xn--,-stbcq.xn--80aswg" == toASCII("лпк,.сайт")
                createAddNegativeParam(getDefaultCounter().withSite2(new CounterMirrorE().withSite("xn--,-stbcq.xn--80aswg")),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withSite2(new CounterMirrorE().withSite("лпк,.сайт")),
                        INVALID_SITE_ONLY_DOMAIN),
                // "xn--et8h.ga" == toASCII("📅.ga")
                createAddNegativeParam(getDefaultCounter().withSite2(new CounterMirrorE().withSite("\uD83D\uDCC5.ga")),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withSite2(new CounterMirrorE().withSite("xn--et8h.ga")),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withMirrors2(Lists.newArrayList(new CounterMirrorE().withSite("!@#$.ru"))),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withMirrors2(Lists.newArrayList(new CounterMirrorE().withSite("xn--,-stbcq.xn--80aswg"))),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withMirrors2(Lists.newArrayList(new CounterMirrorE().withSite("лпк,.сайт"))),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withMirrors2(Lists.newArrayList(new CounterMirrorE().withSite("\uD83D\uDCC5.ga"))),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getDefaultCounter().withMirrors2(Lists.newArrayList(new CounterMirrorE().withSite("xn--et8h.ga"))),
                        INVALID_SITE_ONLY_DOMAIN),
                createAddNegativeParam(getCounterWithExistsNameAndSite(), COUNTER_ALREADY_EXISTS),
                createAddNegativeParam(getCounterWithExistsNameAndSiteAsMirror(), COUNTER_ALREADY_EXISTS),
                createAddNegativeParam(getCounterWithSourceAndExistsNameAndSite(CounterSource.MARKET), COUNTER_ALREADY_EXISTS),
                createAddNegativeParam(getDefaultCounter().withName("\uD83D\uDD95"), NOT_ALLOWED_SYMBOLS_IN_COUNTER_NAME),
                createAddNegativeParam(getDefaultCounter().withFeatures(asList(Feature.ADFOX)), FEATURE_CANT_BE_ENABLED),
                createAddNegativeParam(getDefaultCounter().withFilterRobots(0L), WRONG_ROBOTS)
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(owner);
    }

    @Test
    public void checkTryAddCounter() {
        user.onManagementSteps().onCountersSteps().addCounterAndExpectError(expectedError, counterWrapperToAdd.get());
    }
}
