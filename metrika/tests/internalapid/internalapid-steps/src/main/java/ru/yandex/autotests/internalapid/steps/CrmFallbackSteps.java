package ru.yandex.autotests.internalapid.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.metrika.internalapid.idm.crm.FallbackRequest;
import ru.yandex.metrika.internalapid.idm.crm.FallbackStatus;
import ru.yandex.metrika.internalapid.idm.crm.Reason;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

public class CrmFallbackSteps extends HttpClientLiteFacade {

    protected CrmFallbackSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Включить fallback-режим от имени {0}")
    public Object enableFallback(String login, Reason reason, String reasonText, String solomonLink) {
        return post(Object.class,
                "/crm/fallback/enable",
                new FallbackRequest().withEnabledBy(login).withReasonType(reason).withReasonText(reasonText).withSolomonLink(solomonLink)
        );
    }


    @Step("Выключить fallback-режим от имени {0}")
    public Object disableFallback(String login, Reason reason, String reasonText, String solomonLink) {
        return post(Object.class,
                "/crm/fallback/disable",
                new FallbackRequest().withEnabledBy(login).withReasonType(reason).withReasonText(reasonText).withSolomonLink(solomonLink)
        );
    }

    @Step("Проверить статус fallback-режима")
    public FallbackStatus getStatus() {
        return get(FallbackStatus.class, "/crm/fallback/status");
    }
}
