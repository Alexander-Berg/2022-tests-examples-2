package ru.yandex.autotests.morda.rules;

/**
 * User: asamar
 * Date: 04.09.2015.
 */

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.ArrayList;
import java.util.List;

@Resource.Classpath("morda-rules.properties")
public class MordaRulesProperties {

    @Property("morda.rules.browser.name")
    private String browserName;

    @Property("morda.rules.browser.version")
    private String browserVersion;

    @Property("morda.rules.retry.count")
    private int retryCount;

    @Property("morda.rules.retry.delay")
    private int retryDelay;

    @Property("morda.rules.cookies.override")
    private List<String> cookiesToOverride = new ArrayList<>();

    @Property("morda.rules.cookies.override.yandexuid")
    private String overrideYandexuidCookie;

    @Property("morda.rules.blacklist")
    private List<String> blacklist = new ArrayList<>();

    @Property("morda.rules.headers")
    private List<String> headers = new ArrayList<>();

    @Property("morda.rules.remap")
    private List<String> remap = new ArrayList<>();

    @Property("morda.rules.headers.useragent")
    private String useragent;

    @Property("morda.rules.savevars")
    private boolean saveVars;

    @Property("morda.rules.exp")
    private String exp;

    public MordaRulesProperties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    public String getBrowserName() {
        return browserName;
    }

    public String getBrowserVersion() {
        return browserVersion;
    }

    public int getRetryCount() {
        return retryCount;
    }

    public int getRetryDelay() {
        return retryDelay;
    }

    public String getOverrideYandexuidCookie() {
        return overrideYandexuidCookie;
    }

    public List<String> getCookiesToOverride() {
        return cookiesToOverride;
    }

    public List<String> getBlacklist() {
        return blacklist;
    }

    public List<String> getHeaders() {
        return headers;
    }

    public String getUseragent() {
        return useragent;
    }

    public String getExp() {
        return exp;
    }

    public boolean isSaveVars() {
        return saveVars;
    }

    public List<String> getRemap() {
        return remap;
    }
}