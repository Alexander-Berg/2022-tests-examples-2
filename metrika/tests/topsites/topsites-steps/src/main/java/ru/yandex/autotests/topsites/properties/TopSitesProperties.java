package ru.yandex.autotests.topsites.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

@Resource.Classpath("topsites.properties")
public class TopSitesProperties {

    private static final TopSitesProperties INSTANCE = new TopSitesProperties();

    private TopSitesProperties() {
        PropertyLoader.populate(this);
    }

    public static TopSitesProperties getInstance() {
        return INSTANCE;
    }

    @Property("api.uri")
    private String apiUri;

    public URL getApiUrl() {
        return rethrowFunction((String url) -> new URL(url)).apply(apiUri);
    }
}
