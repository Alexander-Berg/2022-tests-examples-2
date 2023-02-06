package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;

public class HuaweiUpdateParameters extends CommonFrontParameters {

    @FormParameter("client_id")
    private final String clientId;

    @FormParameter("client_secret")
    private final String clientSecret;

    public HuaweiUpdateParameters(String clientId, String clientSecret) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
    }

    public String getClientId() {
        return clientId;
    }

    public String getClientSecret() {
        return clientSecret;
    }
}
