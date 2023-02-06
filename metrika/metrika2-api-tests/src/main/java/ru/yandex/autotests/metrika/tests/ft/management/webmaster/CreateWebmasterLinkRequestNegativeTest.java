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
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLink;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLinkStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterSite;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.WEBMASTER_LINK)
@Title("Создание запроса на привязку домена (негативные тесты)")
public class CreateWebmasterLinkRequestNegativeTest {

    private static final Long WEBMASTER_USER_UID = Users.WEBMASTER_NONEXISTENT_USER.get(User.UID);
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
    @Title("Создаем запрос на привязку, инициированный Метрикой, при уже существующем запросе")
    public void createExistingWebmasterLinkRequestFromMetrika() {
        WebmasterLink createdLink = user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectSuccess(counterId, domain);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assumeThat("Статус запроса - 'Требуется подтверждение Вебмастера'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_WEBMASTER_CONFIRM));

        user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectError(counterId, domain, new CustomError(400L, startsWith("webmaster link already exists")));
    }

    @Test
    @Title("Создаем запрос на привязку, инициированный Вебмастером")
    public void createExistingWebmasterLinkRequestFromWebmaster() {
        WebmasterLink createdLink = intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().createLinkAndExpectSuccess(counterId, domain, WEBMASTER_USER_UID);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assumeThat("Статус запроса - 'Требуется подтверждение Метрики'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_METRIKA_CONFIRM));

        user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectError(counterId, domain, new CustomError(400L, startsWith("webmaster link already exists")));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().deleteLinkAndIgnoreResult(counterId, domain);
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
