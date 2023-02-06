package ru.yandex.autotests.metrika.tests.ft.management.quotas;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.QuotaControllerInnerQuotaEntry;
import ru.yandex.metrika.api.management.client.QuotaControllerInnerQuotaRateEntry;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER_DIRECT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_DEFAULT_QUOTA;

/**
 * Created by sourx on 12.01.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.QUOTAS)
@Title("Проверка ручки лимитов")
@RunWith(Parameterized.class)
public class QuotasTest {

    private UserSteps user;
    private QuotaControllerInnerQuotaEntry actualQuota;
    private QuotaControllerInnerQuotaEntry expectedQuota;

    @Parameter(0)
    public User userEnum;

    @Parameter(1)
    public Long limit;

    @Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                        {USER_WITH_DEFAULT_QUOTA, 5000L},
                        {MANAGER_DIRECT, 5000000L}
                }
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userEnum);

        QuotaControllerInnerQuotaRateEntry expectedLimit = new QuotaControllerInnerQuotaRateEntry()
                .withLimit(limit);

        expectedQuota = new QuotaControllerInnerQuotaEntry()
                .withClientRead(expectedLimit)
                .withClientWrite(expectedLimit)
                .withReportRead(expectedLimit);
    }

    @Test
    @Title("Проверка максимального количества запросов к API")
    public void checkAPIQuotaLimits() {
        actualQuota = user.onManagementSteps().onQuotasSteps().getQuotas().getApi();
        assertThat("объект, который вернул запрос эквивалентен ожидаемому объекту",
                actualQuota, beanEquivalent(expectedQuota));
    }

    @Test
    @Title("Проверка максимального количества запросов к Interface")
    public void checkInterfaceQuotaLimits() {
        actualQuota = user.onManagementSteps().onQuotasSteps().getQuotas().getInterface();
        assertThat("объект, который вернул запрос эквивалентен ожидаемому объекту",
                actualQuota, beanEquivalent(expectedQuota));
    }

}
