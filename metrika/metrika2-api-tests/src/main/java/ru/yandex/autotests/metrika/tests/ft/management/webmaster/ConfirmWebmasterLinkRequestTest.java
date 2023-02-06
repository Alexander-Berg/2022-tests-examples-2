package ru.yandex.autotests.metrika.tests.ft.management.webmaster;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
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
@Title("Подтверждение запроса на привязку домена")
public class ConfirmWebmasterLinkRequestTest {

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
    @Title("Подтверждаем запрос на привязку, инициированный Метрикой")
    public void confirmWebmasterLinkRequestFromMetrika() {
        WebmasterLink createdLink = user.onManagementSteps().onWebmasterLinkPublicSteps().createLinkAndExpectSuccess(counterId, domain);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assumeThat("Статус запроса - 'Требуется подтверждение Вебмастера'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_WEBMASTER_CONFIRM));

        WebmasterLink confirmedLink = intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().confirmLinkAndExpectSuccess(counterId, domain, WEBMASTER_USER_UID);
        assertThat("Статус запроса - 'Подтвержден'", confirmedLink.getStatus(), equalTo(WebmasterLinkStatus.OK));
    }

    @Test
    @Title("Подтверждаем запрос на привязку, инициированный Вебмастером")
    public void confirmWebmasterLinkRequestFromWebmaster() {
        WebmasterLink createdLink = intapiUser.onManagementSteps().onWebmasterLinkInternalSteps().createLinkAndExpectSuccess(counterId, domain, WEBMASTER_USER_UID);
        assumeThat("Запрос на привязку есть в базе", createdLink, notNullValue());
        assumeThat("Статус запроса - 'Требуется подтверждение Метрики'", createdLink.getStatus(), equalTo(WebmasterLinkStatus.NEED_METRIKA_CONFIRM));

        WebmasterLink confirmedLink = user.onManagementSteps().onWebmasterLinkPublicSteps().confirmLinkAndExpectSuccess(counterId, domain);
        assertThat("Статус запроса - 'Подтвержден'", confirmedLink.getStatus(), equalTo(WebmasterLinkStatus.OK));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onWebmasterLinkPublicSteps().deleteLinkAndIgnoreResult(counterId, domain);
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
