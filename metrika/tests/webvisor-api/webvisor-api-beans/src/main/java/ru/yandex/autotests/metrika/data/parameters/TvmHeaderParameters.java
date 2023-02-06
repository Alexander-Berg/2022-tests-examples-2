package ru.yandex.autotests.metrika.data.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class TvmHeaderParameters extends AbstractFormParameters {
    @FormParameter("X-Ya-Service-Ticket")
    private String serviceTicket;

    @FormParameter("X-Ya-User-Ticket")
    private String userTicket;

    public String getServiceTicket() {
        return serviceTicket;
    }

    public TvmHeaderParameters withServiceTicket(String serviceTicket) {
        this.serviceTicket = serviceTicket;
        return this;
    }

    public String getUserTicket() {
        return userTicket;
    }

    public TvmHeaderParameters withUserTicket(String userTicket) {
        this.userTicket = userTicket;
        return this;
    }
}
