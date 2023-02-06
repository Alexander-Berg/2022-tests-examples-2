package ru.yandex.autotests.metrika.properties;

import ru.yandex.autotests.metrika.data.common.handles.SegmentsPathFragment;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URL;

import static ru.yandex.autotests.metrika.utils.Utils.toUrl;

/**
 * Created by proxeter (Nikolay Mulyar - proxeter@yandex-team.ru) on 02.07.2014.
 */
@Resource.Classpath("metrikaapi.properties")
public class MetrikaApiProperties {

    private static MetrikaApiProperties instance;

    /**
     * URL по которому находится API тестируемой системы (отчеты, управлние и пр.)
     * <p>
     * строка вида scheme://host:port
     */
    @Property("api.testing")
    private String apiTesting;

    /**
     * URL по которому находится API эталонной системы (отчеты, управлние и пр.)
     * <p>
     * строка вида scheme://host:port
     */
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

    @Property("api.default.double.delta")
    private Double doubleDelta;

    @Property("api.semaphore.name.prefix")
    private String apiSemaphoreNamePrefix;

    private MetrikaApiProperties() {
        PropertyLoader.populate(this);
    }


    public static MetrikaApiProperties getInstance() {
        if (instance == null) {
            instance = new MetrikaApiProperties();
        }

        return instance;
    }
    public URL getApiTesting() {
        return toUrl(apiTesting);
    }

    public URL getApiReference() {
        return toUrl(apiReference);
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

    public SegmentsPathFragment getApiSegmentsType() {
        return SegmentsPathFragment.valueOf(apiSegmentsType);
    }

    public Integer getApiSemaphorePermits() {
        return apiSemaphorePermits;
    }

    public String getApiSemaphoreNamePrefix() {
        return apiSemaphoreNamePrefix;
    }

    public Double getDoubleDelta() {
        return doubleDelta;
    }

    public static void main(String[] args) {
        System.out.println("1".split(",", 0).length);
    }
}
