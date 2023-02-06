package ru.yandex.autotests.metrika.tests.ft.report.metrika.authorization;

import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_EMPTY_TOKEN;

/**
 * Created by okunev on 24.11.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.AUTHORIZATION})
@Title("Авторизация: без токена")
public class NoOauthTokenTest extends AuthorizationBaseTest {

    @BeforeClass
    public static void beforeClass() {
        user.withUser(USER_WITH_EMPTY_TOKEN)
                .withRequestSource("api");
    }

    @Test
    public void tableAuthorizationCheckOwnCounter() {
        user.onReportSteps().getTableReportAndExpectError(ManagementError.ACCESS_DENIED,
                getReportParameters().withId(ownCounter.get(ID)));
    }

    @Test
    public void tableAuthorizationCheckAccessibleCounter() {
        user.onReportSteps().getTableReportAndExpectError(ManagementError.ACCESS_DENIED,
                getReportParameters().withId(accessibleCounter.get(ID)));
    }

    @Test
    public void tableAuthorizationTokenCheckPrivateCounter() {
        user.onReportSteps().getTableReportAndExpectError(ManagementError.ACCESS_DENIED,
                getReportParameters().withId(privateCounter.get(ID)));
    }
}
