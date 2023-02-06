package ru.yandex.autotests.tuneclient;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URI;

@Resource.Classpath("tune.properties")
public class Properties {

    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Property("tune.baseURI")
    protected URI baseURI;

    @Property("tune.geo.path")
    protected String geoPath;

    @Property("tune.lang.path")
    protected String langPath;

    @Property("tune.my.path")
    protected String myPath;

    @Property("tune.region.path")
    protected String regionPath;


    public URI getBaseURI() {
        return baseURI;
    }

    public String getGeoPath() {
        return geoPath;
    }

    public String getLangPath() {
        return langPath;
    }

    public String getMyPath() {
        return myPath;
    }

    public String getRegionPath() {
        return regionPath;
    }
}
