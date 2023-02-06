package ru.yandex.autotests.metrika.appmetrica.parameters;

import static org.apache.http.HttpHeaders.AUTHORIZATION;
import static org.apache.http.HttpHeaders.CONTENT_TYPE;

public class CommonHeaders extends FreeFormParameters {

    public CommonHeaders withOAuthToken(String token) {
        append(AUTHORIZATION, token == null ? null : "OAuth " + token);
        return this;
    }

    public CommonHeaders withPostApiKey(String postApiKey) {
        append(AUTHORIZATION, postApiKey == null ? null : "Post-Api-Key " + postApiKey);
        return this;
    }

    public CommonHeaders withContentType(String contentType) {
        append(CONTENT_TYPE, contentType);
        return this;
    }
}
