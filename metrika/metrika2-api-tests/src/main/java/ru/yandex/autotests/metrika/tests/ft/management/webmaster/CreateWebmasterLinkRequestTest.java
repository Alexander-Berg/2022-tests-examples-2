package ru.yandex.autotests.metrika.tests.ft.management.webmaster;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLink;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLinkStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterSite;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.WEBMASTER_LINK)
@Title("Создание запроса на привязку домена")
public class CreateWebmasterLinkRequestTest {

    private static final Long WEBMASTER_USER_UID = Users.WEBMASTER_NONEXISTENT_USER.get(User.UID);
    private UserSteps user = new UserSteps().withUser(Users.SIMPLE_USER);
    private UserSteps intapiUser = new UserSteps().withUser(Users.SUPER_USER);
    private Long counterId;
    private String domain;

    @Before
    public void setup() {
        domain = getCounterSite();
        CounterFull counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(new CounterFull()
                .withSite("www." + domain));
        counterId = counter.getId();
    }

    @Test
    @Title("Создаем запрос на привязку, инициированный Метрикой")
    public void createWebmasterLinkRequestFromMetrika() {
        WebmasterLink createdLink = user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectSuccess(counterId, domain);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assertThat("Статус запроса - 'Требуется подтверждение Вебмастера'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_WEBMASTER_CONFIRM));
    }

    @Test
    @Title("Создаем запрос на привязку, инициированный Вебмастером")
    public void createWebmasterLinkRequestFromWebmaster() {
        intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().createLinkAndExpectSuccess(counterId, domain, WEBMASTER_USER_UID);
        WebmasterLink createdLink = user.onManagementSteps().onWebmasterLinkPublicSteps().getLinkInfoAndExpectSuccess(counterId, domain);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assertThat("Статус запроса - 'Требуется подтверждение Метрики'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_METRIKA_CONFIRM));
    }

    @Test
    @Title("Проверяем, что созданный запрос есть в метаданных счетчика")
    public void checkMirrors2Field() {
        intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().createLinkAndExpectSuccess(counterId, domain, WEBMASTER_USER_UID);
        WebmasterLink createdLink = user.onManagementSteps().onWebmasterLinkPublicSteps().getLinkInfoAndExpectSuccess(counterId, domain);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assumeThat("Статус запроса - 'Требуется подтверждение Метрики'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_METRIKA_CONFIRM));

        CounterFull counterInfo = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId);
        CounterMirrorE cm = counterInfo.getMirrors2().stream().filter(c -> c.getDomain().equals(domain)).findAny().orElse(null);
        if (cm == null && counterInfo.getSite2().getDomain().equals(domain)) {
            cm = counterInfo.getSite2();
        }
        assumeThat("В ответе ручки счетчика есть этот домен", cm, notNullValue());
        assertThat("Статус привязки домена отобразился корректно", cm.getStatus(), equalTo(WebmasterLinkStatus.NEED_METRIKA_CONFIRM));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().deleteLinkAndIgnoreResult(counterId, domain);
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
