package ru.yandex.autotests.widgets.rule;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import net.lightbody.bmp.proxy.http.RequestInterceptor;
import org.apache.http.Header;

import java.util.ArrayList;
import java.util.List;

/**
 * User: ivannik
 * Date: 01.08.13
 * Time: 18:24
 */
public class UriInterceptor implements RequestInterceptor {

    private List<String> uriList = new ArrayList<String>();
    private String host;

    public UriInterceptor(String host) {
        this.host = host;
    }

    @Override
    public void process(BrowserMobHttpRequest request, Har har) {
        Header hostHeader = request.getMethod().getFirstHeader("Host");
        if (hostHeader != null &&
                hostHeader.getValue().contains(host)) {
            uriList.add(request.getMethod().getRequestLine().getUri());
        }
    }

    public List<String> getUriList() {
        return uriList;
    }

    public void resetUri() {
        this.uriList.clear();
    }
}
