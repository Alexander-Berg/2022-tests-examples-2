package ru.yandex.autotests.metrika.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * Created by konkov on 07.05.2015.
 */
@Resource.Classpath("httpclient.properties")
public class HttpClientProperties {
    private static HttpClientProperties instance;

    private HttpClientProperties() {
        PropertyLoader.populate(this);
    }

    public static HttpClientProperties getInstance() {
        if (instance == null) {
            instance = new HttpClientProperties();
        }
        return instance;
    }

    /**
     * таймаут сокета, мс
     */
    @Property("httpclient.socket.timeout")
    private int socketTimeout;

    /**
     * таймаут соединения, мс
     */
    @Property("httpclient.connect.timeout")
    private int connectTimeout;

    /**
     * таймаут на выполнение запроса целиком, мс
     */
    @Property("httpclient.execution.timeout")
    private int executionTimeout;

    public int getSocketTimeout() {
        return socketTimeout;
    }

    public int getConnectTimeout() {
        return connectTimeout;
    }

    public int getExecutionTimeout() {
        return executionTimeout;
    }
}
