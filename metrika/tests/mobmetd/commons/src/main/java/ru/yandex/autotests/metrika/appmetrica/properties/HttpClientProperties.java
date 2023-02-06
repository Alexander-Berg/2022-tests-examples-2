package ru.yandex.autotests.metrika.appmetrica.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

@Resource.Classpath("httpclient.properties")
public class HttpClientProperties {
    private static final HttpClientProperties INSTANCE = new HttpClientProperties();

    private HttpClientProperties() {
        PropertyLoader.populate(this);
    }

    public static HttpClientProperties getInstance() {
        return INSTANCE;
    }

    /**
     * таймаут соединения, с
     */
    @Property("httpclient.connect.timeout")
    private int connectTimeout;

    /**
     * таймаут чтения, с
     */
    @Property("httpclient.read.timeout")
    private int readTimeout;

    /**
     * таймаут выполнения запроса, с
     */
    @Property("httpclient.execution.timeout")
    private int executionTimeout;

    public int getConnectTimeout() {
        return connectTimeout;
    }

    public int getReadTimeout() {
        return readTimeout;
    }

    public int getExecutionTimeout() {
        return executionTimeout;
    }
}
