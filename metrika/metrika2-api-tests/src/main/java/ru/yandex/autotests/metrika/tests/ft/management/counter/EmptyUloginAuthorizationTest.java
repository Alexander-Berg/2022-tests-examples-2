package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.EMPTY_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;

/**

 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Доступность списка счетчиков при пустом ulogin")
public class EmptyUloginAuthorizationTest {

    private UserSteps user = new UserSteps().withDefaultAccuracy().withUser(SIMPLE_USER);

    @Test
    public void noAdvertisingReportWithPublicStatTest() {
        user.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(ulogin(EMPTY_USER));
    }
}
