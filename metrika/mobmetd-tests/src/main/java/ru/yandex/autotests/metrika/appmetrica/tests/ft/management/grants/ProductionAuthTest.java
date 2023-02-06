package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.grants;

import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Issues;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.UNAUTHORIZED;

@Features(Requirements.Feature.AUTH)
@Stories(Requirements.Story.AUTH)
@Issues(
        @Issue("MOBMET-6702")
)
@Title("Проверка авторизации через uid_real в публичном API")
public final class ProductionAuthTest {

    private static UserSteps prodWithToken = UserSteps.onProductionWithToken(SIMPLE_USER);

    private static UserSteps prodWithUid = UserSteps.onProductionWithUid(SIMPLE_USER);

    @Test
    public void checkTokenAuthWorksInProduction() {
        prodWithToken.onApplicationSteps().getApplications();
    }

    @Test
    public void checkUidAuthDoesntWorkInProduciton() {
        prodWithUid.onApplicationSteps().getApplicationsAndExpectError(UNAUTHORIZED);
    }
}
