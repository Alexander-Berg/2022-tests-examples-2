package ru.yandex.autotests.metrika.data.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CommonHeaders extends AbstractFormParameters {

    @FormParameter("Authorization")
    private String oauthTokenHeader;

    public String getOauthTokenHeader() {
        return oauthTokenHeader;
    }

    public CommonHeaders withOAuthToken(String token) {
        oauthTokenHeader = token == null ? null : "OAuth " + token;
        return this;
    }
}
