package ru.yandex.autotests.internalapid.properties;

import ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.MalformedURLException;
import java.net.URL;

import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

@Resource.Classpath("internalapid.properties")
public class InternalApiProperties {

    private static final InternalApiProperties INSTANCE = new InternalApiProperties();

    private InternalApiProperties() {
        PropertyLoader.populate(this);
    }

    public static InternalApiProperties getInstance() {
        return INSTANCE;
    }

    @Property("api.uri")
    private String apiUri;

    public URL getApiUrl() {
        return rethrowFunction((LambdaExceptionUtil.Function_WithExceptions<String, URL, MalformedURLException>) URL::new)
                .apply(System.getProperty("apiUrl", apiUri));
    }

    @Property("api.ref.uri")
    private String apiRefUri;

    public URL getApiRefUrl() {
        return rethrowFunction((LambdaExceptionUtil.Function_WithExceptions<String, URL, MalformedURLException>) URL::new)
                .apply(System.getProperty("apiRefUrl", apiRefUri));
    }
}

















