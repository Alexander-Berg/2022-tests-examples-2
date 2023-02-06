package ru.yandex.autotests.metrika.appmetrica.core;

import java.util.List;

/**
 * @author dancingelf
 */
public class AppMetricaCsvResponse<T> {

    private final List<String> headers;
    private final List<T> content;

    public AppMetricaCsvResponse(List<String> headers, List<T> content) {
        this.headers = headers;
        this.content = content;
    }

    public List<String> getHeaders() {
        return headers;
    }

    public List<T> getContent() {
        return content;
    }
}
