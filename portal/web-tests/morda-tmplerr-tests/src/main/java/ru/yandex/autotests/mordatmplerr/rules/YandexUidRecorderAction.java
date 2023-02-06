package ru.yandex.autotests.mordatmplerr.rules;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import net.lightbody.bmp.proxy.http.RequestInterceptor;
import org.apache.http.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;
import ru.yandex.autotests.utils.morda.cookie.Cookie;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.03.14
 */
public class YandexUidRecorderAction implements ProxyAction {
    private Set<String> allYandexUids = new HashSet<>();

    public boolean isNeeded() {
        return true;
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.addRequestInterceptor(new RequestInterceptor() {
            @Override
            public void process(BrowserMobHttpRequest request, Har har) {
                for (Header header : request.getMethod().getHeaders("Cookie")) {
                    List<String> cookies = Arrays.asList(header.getValue().split("; "));
                    for (String cookie : cookies) {
                        String[] c = cookie.split("=");
                        if (c[0].equals(Cookie.YANDEXUID.getName())) {
                            allYandexUids.add(c[1]);
                        }
                    }
                }
            }
        });
    }

    public Set<String> getAllYandexUids() {
        return allYandexUids;
    }
}
