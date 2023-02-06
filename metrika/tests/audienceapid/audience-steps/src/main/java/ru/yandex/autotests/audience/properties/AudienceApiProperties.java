package ru.yandex.autotests.audience.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

/**
 * Created by konkov on 23.03.2017.
 */
@Resource.Classpath("audienceapi.properties")
public class AudienceApiProperties {

    private static final AudienceApiProperties INSTANCE = new AudienceApiProperties();

    private AudienceApiProperties() {
        PropertyLoader.populate(this);
    }

    public static AudienceApiProperties getInstance() {
        return INSTANCE;
    }

    /**
     * URL по которому отвечает демон audienceapid
     */
    @Property("api.uri")
    private String apiUri;

    public URL getApiUrl() {
        return rethrowFunction((String url) -> new URL(url)).apply(apiUri);
    }
}
