package ru.yandex.autotests.mordabackend;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * User: eroshenkoam
 * Date: 11/8/13, 1:57 PM
 */
@Resource.Classpath("morda-backend.properties")
public class Properties extends BaseProperties {

    public Properties() {
        super();
        ConvertUtils.register(new ListConverter(","), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("thread.cnt")
    protected int threadCnt = Runtime.getRuntime().availableProcessors();

    @Property("morda.server.host")
    protected String mordaServerHost;

    @Property("cookies")
    private List<String> cookies = new ArrayList<>();

    public int getThreadCnt() {
        return threadCnt;
    }

    public String getMordaServerHost() {
        return mordaServerHost;
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
}
