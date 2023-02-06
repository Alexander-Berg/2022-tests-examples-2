package ru.yandex.autotests.mordacommonsteps;


import org.apache.commons.beanutils.ConvertUtils;
import org.openqa.selenium.Platform;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Cookie;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

@Resource.Classpath("config.properties")
public class Properties {
    public Properties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("user.agent")
    private String userAgent;

    @Property("max.retries")
    private int maxRetries = 1;

    @Property("retry.delay")
    private int retryDelay = 0;

    @Property("hosts.to.remap")
    private List<String> hostsToRemap = new ArrayList<>();

    @Property("cookies")
    private List<String> cookies = new ArrayList<>();

    @Property("headers")
    private List<String> headers = new ArrayList<>();

    @Property("blackList")
    private List<String> blackList = new ArrayList<>();

    @Property("use.proxy")
    private boolean useProxy = false;

    @Property("browser.name")
    private String browserName;

    @Property("browser.version")
    private String browserVersion = "";

    @Property("webdriver.base.url")
    private URL baseURL;
    
    @Property("grid.retry.delay")
    private int gridRetryDelay = 0;

    public String getUserAgent() {
        return userAgent;
    }

    public List<String> getBlackList() {
        return blackList;
    }

    public int getMaxRetries() {
        return maxRetries;
    }

    public int getRetryDelay() {
        return retryDelay;
    }

    public void setUserAgent(String userAgent) {
        this.userAgent = userAgent;
    }

    public DesiredCapabilities getCapabilities() {
        if (browserName != null) {
            return new DesiredCapabilities(browserName, browserVersion, Platform.ANY);
        } else {
            return DesiredCapabilities.firefox();
        }
    }

    public Map<Pattern, String> getRemap() {
       Map<Pattern, String> remap = new HashMap<>();
        try {
            for (String str : hostsToRemap) {
                String[] s = str.split(":");
                remap.put(Pattern.compile(s[0]), s[1]);
            }
        } catch (Exception e) {
            throw new RuntimeException("Host remaping data is incorrect", e);
        }
        return remap;
    }

    public Set<Cookie> getCookies() {
        Set<Cookie> result = new HashSet<>();
        for (String str : cookies) {
            String[] cookie = str.split("=");
            if (cookie.length != 2) {
                throw new IllegalArgumentException("Incorrect data for cookie: " + str);
            }
            result.add(new Cookie(cookie[0], cookie[1]));
        }
        return result;
    }

    public Set<Header> getHeaders() {
        Set<Header> result = new HashSet<>();
        for (String str : headers) {
            String[] header = str.split("=");
            if (header.length != 2) {
                throw new IllegalArgumentException("Incorrect data for header: " + str);
            }
            result.add(new Header(header[0], header[1]));
        }
        return result;
    }

    public boolean isUseProxy() {
        return useProxy;
    }

    public URL getBaseURL() {
        return baseURL;
    }
    
    public int getGridRetryDelay() {
        return gridRetryDelay;
    }

    public String getBrowserName() {
        return browserName;
    }

    public String getBrowserVersion() {
        return browserVersion;
    }

}