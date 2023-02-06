package ru.yandex.metrika.clickhouse.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;

import static com.google.common.base.Throwables.throwIfUnchecked;

@Resource.Classpath("clickhouse.statbox.properties")
public class ClickhouseStatBoxB2BTestsProperties {

    private static final ClickhouseStatBoxB2BTestsProperties INSTANCE = new ClickhouseStatBoxB2BTestsProperties();

    @Property("queries.base.dir")
    private String queriesBaseDir;

    @Property("uri.test")
    private String uriTest;

    private URL uriTest_;

    @Property("uri.ref")
    private String uriRef;

    private URL uriRef_;

    @Property("user")
    private String user;

    @Property("password")
    private String password;

    @Property("tolerance")
    private boolean tolerance;

    @Property("max.abs.diff")
    private double maxAbsDiff;

    public ClickhouseStatBoxB2BTestsProperties() {
        PropertyLoader.populate(this);
        init();
    }

    private void init() {
        uriTest_ = toUrl(uriTest);
        uriRef_ = toUrl(uriRef);
    }

    public static ClickhouseStatBoxB2BTestsProperties getInstance() {
        return INSTANCE;
    }

    public Path getQueriesBaseDir() {
        return Paths.get(queriesBaseDir).toAbsolutePath();
    }

    public URL getUriTest() {
        return uriTest_;
    }

    public URL getUriRef() {
        return uriRef_;
    }

    public String getUser() {
        return user;
    }

    public String getPassword() {
        return password;
    }

    public boolean isTolerance() {
        return tolerance;
    }

    public double getMaxAbsDiff() {
        return maxAbsDiff;
    }

    private static URL toUrl(String url) {
        try {
            return new URL(url);
        } catch (MalformedURLException e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }
}
