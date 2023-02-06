package ru.yandex.autotests.mordalinks;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URI;

@Resource.Classpath("config.properties")
public class Properties {

    public Properties() {
        PropertyLoader.populate(this);
    }

    @Property("links.host")
    private URI linksHost = URI.create("http://portal.haze.yandex.net");

    public URI getLinksHost() {
        return linksHost;
    }
}