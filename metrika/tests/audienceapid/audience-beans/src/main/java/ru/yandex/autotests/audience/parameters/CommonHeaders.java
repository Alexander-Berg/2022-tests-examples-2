package ru.yandex.autotests.audience.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CommonHeaders extends AbstractFormParameters {

    @FormParameter("Authorization")
    private String oauthTokenHeader;
    @FormParameter("X-Ya-Service-Ticket")
    private String serviceTicketHeader;
    @FormParameter("X-Ya-User-Ticket")
    private String userTicketHeader;

    public String getOauthTokenHeader() {
        return oauthTokenHeader;
    }

    public String getServiceTicketHeader() {
        return serviceTicketHeader;
    }

    public String getUserTicketHeader() {
        return userTicketHeader;
    }

    public CommonHeaders withOAuthToken(String token) {
        oauthTokenHeader = token == null ? null : "OAuth " + token;
        return this;
    }
    public CommonHeaders withServiceTicket(String token) {
        serviceTicketHeader = token;
        return this;
    }
    public CommonHeaders withUserTicket(String token) {
        userTicketHeader = token;
        return this;
    }
}
