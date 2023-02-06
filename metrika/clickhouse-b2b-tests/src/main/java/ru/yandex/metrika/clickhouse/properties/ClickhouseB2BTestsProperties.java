package ru.yandex.metrika.clickhouse.properties;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

import static com.google.common.base.Throwables.throwIfUnchecked;

@Resource.Classpath("clickhouse.b2b.properties")
public class ClickhouseB2BTestsProperties {

    private static final Gson GSON  = new GsonBuilder().create();
    private static final ClickhouseB2BTestsProperties INSTANCE = new ClickhouseB2BTestsProperties();

    @Property("requests.base.dir")
    private String requestsBaseDir;

    @Property("faced.api.test")
    private String facedApiTest;

    private URL facedApiTest_;

    @Property("faced.api.ref")
    private String facedApiRef;

    private URL facedApiRef_;

    @Property("mobmetd.api.test")
    private String mobmetdApiTest;

    private URL mobmetdApiTest_;

    @Property("mobmetd.api.ref")
    private String mobmetdApiRef;

    private URL mobmetdApiRef_;

    @Property("faced.vault.secretid")
    private String facedVaultSecretId;

    @Property("faced.vault.secretkey")
    private String facedVaultSecretKey;

    private String facedOauthToken;

    @Property("mobmetd.vault.secretid")
    private String mobmetdVaultSecretId;

    @Property("mobmetd.vault.secretkey")
    private String mobmetdVaultSecretKey;

    private String mobmetdOauthToken;

    @Property("faced.handles.include")
    private String facedHandlesInclude;

    @Property("faced.handles.exclude")
    private String facedHandlesExclude;

    @Property("mobmetd.handles.include")
    private String mobmetdHandlesInclude;

    @Property("mobmetd.handles.exclude")
    private String mobmetdHandlesExclude;

    @Property("start.date")
    private String startDate;

    @Property("finish.date")
    private String finishDate;

    @Property("limit.absolute")
    private int absoluteLimit;

    @Property("limit.relative")
    private double relativeLimit;

    @Property("target.dir")
    private String targetDir;

    @Property("fork.pool.size")
    private int forkPoolSize;

    public ClickhouseB2BTestsProperties() {
        PropertyLoader.populate(this);
        init();
    }

    private void init() {
        facedApiTest_ = toUrl(facedApiTest);
        facedApiRef_ = toUrl(facedApiRef);
        mobmetdApiRef_ = toUrl(mobmetdApiRef);
        mobmetdApiTest_ = toUrl(mobmetdApiTest);

        facedOauthToken = loadOauthToken(facedVaultSecretId, facedVaultSecretKey);
        mobmetdOauthToken = loadOauthToken(mobmetdVaultSecretId, mobmetdVaultSecretKey);
    }

    private String loadOauthToken(String secretId, String key) {
        Map<String, String> secretContent = VaultClient.loadLastVersion(secretId);
        Map<String, String> deserializedSecret = GSON.fromJson(secretContent.get(key), new TypeToken<Map<String, String>>() {}.getType());
        return deserializedSecret.get("oauth_token");
    }

    public static ClickhouseB2BTestsProperties getInstance() {
        return INSTANCE;
    }

    public String getRequestsBaseDir() {
        return requestsBaseDir;
    }

    public URL getFacedApiTest() {
        return facedApiTest_;
    }

    public URL getFacedApiRef() {
        return facedApiRef_;
    }

    public URL getMobmetdApiTest() {
        return mobmetdApiTest_;
    }

    public URL getMobmetdApiRef() {
        return mobmetdApiRef_;
    }

    public String getFacedOauthToken() {
        return facedOauthToken;
    }

    public String getMobmetdOauthToken() {
        return mobmetdOauthToken;
    }

    public String getFacedHandlesInclude() {
        return facedHandlesInclude;
    }

    public String getFacedHandlesExclude() {
        return facedHandlesExclude;
    }

    public String getMobmetdHandlesInclude() {
        return mobmetdHandlesInclude;
    }

    public String getMobmetdHandlesExclude() {
        return mobmetdHandlesExclude;
    }

    public String getStartDate() {
        return startDate;
    }

    public String getFinishDate() {
        return finishDate;
    }

    public int getAbsoluteLimit() {
        return absoluteLimit;
    }

    public double getRelativeLimit() {
        return relativeLimit;
    }

    public String getTargetDir() {
        return targetDir;
    }

    public int getForkPoolSize() {
        return forkPoolSize;
    }

    private static URL toUrl(String url) {
        if (url == null) {
            return null;
        }

        try {
            return new URL(url);
        } catch (MalformedURLException e) {
            throwIfUnchecked(e);
            throw new RuntimeException(e);
        }
    }
}
