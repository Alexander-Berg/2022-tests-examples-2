package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.*;
import org.apache.commons.lang.StringUtils;
import org.apache.http.Header;
import org.apache.http.StatusLine;
import org.apache.http.message.BasicHeader;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

import java.util.Set;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public class CookieAction extends ConfigProxyAction<Set<Cookie>>
        implements MergeableProxyAction<Set<Cookie>>, ReplaceableProxyAction<Set<Cookie>> {

    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(CookieAction.class);
    private static final String SET_COOKIE_HEADER = "Set-Cookie";

    private CookieAction() {
        super(CONFIG.getCookies());
    }

    @Override
    public boolean isNeeded() {
        return !data.isEmpty();
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        LOG.info("Cookies pre-set: \n" + StringUtils.join(data, "\n"));
        proxyServer.addRequestInterceptor(new RequestInterceptor() {
            @Override
            public void process(BrowserMobHttpRequest request, Har har) {
                final RequestCallback callback = request.getRequestCallback();
                request.setRequestCallback(new RequestCallback() {
                    @Override
                    public void handleStatusLine(StatusLine statusLine) {
                        callback.handleStatusLine(statusLine);
                    }

                    @Override
                    public void handleHeaders(Header[] headers) {
                        for (int i = 0; i < headers.length; i++) {
                            if (headers[i].getName().equals(SET_COOKIE_HEADER)) {
                                headers[i] = new BasicHeader(
                                        headers[i].getName(),
                                        replaceSetCookie(headers[i].getValue()));
                            }
                        }
                        callback.handleHeaders(headers);
                    }

                    @Override
                    public boolean reportHeader(Header header) {
                        return callback.reportHeader(header);
                    }

                    @Override
                    public void reportError(Exception e) {
                        callback.reportError(e);
                    }
                });
            }
        });
    }

    private String replaceSetCookie(String header) {
        for (Cookie c : data) {
            if (header.startsWith(c.getName())) {
                return header.replaceAll("(?<=^\\Q" + c.getName() + "\\E=)[^;]+(?=;.*)", c.getValue());
            }
        }
        return header;
    }

    @Override
    public void mergeWith(Set<Cookie> data) {
        this.data.addAll(data);
    }

    @Override
    public void replaceWith(Set<Cookie> data) {
        this.data = data;
    }

    static CookieAction cookies() {
        return new CookieAction();
    }
}
