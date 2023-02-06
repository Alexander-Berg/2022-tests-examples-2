package ru.yandex.autotests.audience.internal.api.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

@Resource.Classpath("audienceintapi.properties")
public class AudienceInternalApiProperties {

    private static final AudienceInternalApiProperties INSTANCE = new AudienceInternalApiProperties();

    private AudienceInternalApiProperties() {
        PropertyLoader.populate(this);
    }

    public static AudienceInternalApiProperties getInstance() {
        return INSTANCE;
    }

    @Property("api.uri")
    private String apiUri;

    public URL getApiUrl() {
        return rethrowFunction((String url) -> new URL(url)).apply(apiUri);
    }
}
