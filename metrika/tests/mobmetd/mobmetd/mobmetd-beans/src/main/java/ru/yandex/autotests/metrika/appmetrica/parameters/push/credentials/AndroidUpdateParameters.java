package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;


public class AndroidUpdateParameters extends CommonFrontParameters {

    @FormParameter("auth_key")
    private final String authKey;

    public AndroidUpdateParameters(String authKey) {
        this.authKey = authKey;
    }

    public String getAuthKey() {
        return authKey;
    }
}
