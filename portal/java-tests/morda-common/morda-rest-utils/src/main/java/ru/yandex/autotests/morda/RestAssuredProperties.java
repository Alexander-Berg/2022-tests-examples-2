package ru.yandex.autotests.morda;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * Created by wwax on 07.09.16.
 */
@Resource.Classpath("restassured.properties")
public class RestAssuredProperties {
    public RestAssuredProperties() {
        PropertyLoader.populate(this);
    }

    @Property("restassured.dns.override")
    private String dnsOverride = "default";

    public String getDnsOverride() {
        return dnsOverride;
    }
}
