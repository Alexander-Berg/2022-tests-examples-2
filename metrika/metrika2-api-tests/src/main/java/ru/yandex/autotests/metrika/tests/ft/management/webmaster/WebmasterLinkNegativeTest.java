package ru.yandex.autotests.metrika.tests.ft.management.webmaster;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterSite;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.WEBMASTER_LINK)
@Title("Негативные тесты интеграции с Вебмастером")
public class WebmasterLinkNegativeTest {

    private static final Long WEBMASTER_USER_UID = Users.WEBMASTER_NONEXISTENT_USER.get(User.UID);
    private static final String UNKNOWN_DOMAIN = "000nonexistent111.com";
    private UserSteps user = new UserSteps().withUser(Users.SIMPLE_USER);
    private UserSteps intapiUser = new UserSteps().withUser(Users.SUPER_USER);
    private Long counterId;
    private String domain;

    @Before
    public void setup() {
        CounterFull counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(new CounterFull()
                .withSite(getCounterSite()));
        counterId = counter.getId();
        domain = counter.getSite();
    }

    @Test
    @Title("Удаление несуществующей привязки из Метрики")
    public void deleteUnexistingWebmasterLinkFromMetrika() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().deleteLinkAndExpectError(counterId, domain,
                new CustomError(400L, startsWith("Trying to delete nonexistent webmaster link")));
    }

    @Test
    @Title("Удаление несуществующей привязки из Вебмастера")
    public void deleteUnexistingWebmasterLinkFromWebmaster() {
        intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().deleteLinkAndExpectError(counterId, domain, WEBMASTER_USER_UID,
                new CustomError(400L, startsWith("Trying to delete nonexistent webmaster link")));
    }

    @Test
    @Title("Создание запроса по неизвестному домену из Метрики")
    public void createRequestForWrongDomainFromMetrika() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectError(counterId, UNKNOWN_DOMAIN,
                new CustomError(400L, both(startsWith("domain")).and(containsString("doesn't belong to counter"))));
    }

    @Test
    @Title("Создание запроса по неизвестному домену из Вебмастера")
    public void createRequestForWrongDomainFromWebmaster() {
        intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().createLinkAndExpectError(counterId, UNKNOWN_DOMAIN, WEBMASTER_USER_UID,
                new CustomError(400L, both(startsWith("domain")).and(containsString("doesn't belong to counter"))));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().deleteLinkAndIgnoreResult(counterId, domain);
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
