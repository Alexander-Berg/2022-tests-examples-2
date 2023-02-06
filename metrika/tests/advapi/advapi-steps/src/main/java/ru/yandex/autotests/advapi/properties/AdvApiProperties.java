package ru.yandex.autotests.advapi.properties;

import ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.MalformedURLException;
import java.net.URL;

import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

@Resource.Classpath("advapi.properties")
public class AdvApiProperties {

    private static final AdvApiProperties INSTANCE = new AdvApiProperties();

    private AdvApiProperties() {
        PropertyLoader.populate(this);
    }

    public static AdvApiProperties getInstance() {
        return INSTANCE;
    }

    @Property("api.uri")
    private String apiUri;

    @Property("api.default.double.delta")
    private Double doubleDelta;

    @Property("api.testing")
    private String apiTesting;

    @Property("api.reference")
    private String apiReference;

    @Property("b2b.ignoredFields")
    private String[] ignoredFields;

    @Property("b2b.defaultIgnoredFields")
    private String[] defaultIgnoredFields;

    @Property("api.default.accuracy")
    private String defaultAccuracy;

    @Property("api.segments.type")
    private String apiSegmentsType;

    @Property("api.semaphore.permits")
    private Integer apiSemaphorePermits;

    @Property("api.semaphore.name.prefix")
    private String apiSemaphoreNamePrefix;

    public URL getApiUrl() {
        return rethrowFunction((LambdaExceptionUtil.Function_WithExceptions<String, URL, MalformedURLException>) URL::new).apply(apiUri);
    }

    public Double getDoubleDelta() {
        return doubleDelta;
    }

    public String getApiTesting() {
        return apiTesting;
    }

    public String getApiReference() {
        return apiReference;
    }

    public String[] getIgnoredFields() {
        return ignoredFields;
    }

    public String[] getDefaultIgnoredFields() {
        return defaultIgnoredFields;
    }

    public String getDefaultAccuracy() {
        return defaultAccuracy;
    }

    public String getApiSegmentsType() {
        return apiSegmentsType;
    }

    public Integer getApiSemaphorePermits() {
        return apiSemaphorePermits;
    }

    public String getApiSemaphoreNamePrefix() {
        return apiSemaphoreNamePrefix;
    }
}
