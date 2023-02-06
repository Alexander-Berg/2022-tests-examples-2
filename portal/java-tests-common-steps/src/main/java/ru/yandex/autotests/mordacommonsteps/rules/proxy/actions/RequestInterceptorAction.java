package ru.yandex.autotests.mordacommonsteps.rules.proxy.actions;

import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.RequestInterceptor;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public class RequestInterceptorAction implements ProxyAction {
    private static final Logger LOG = Logger.getLogger(RequestInterceptorAction.class);
    private RequestInterceptor requestInterceptor;

    public RequestInterceptorAction(RequestInterceptor requestInterceptor) {
        this.requestInterceptor = requestInterceptor;
    }

    @Override
    public boolean isNeeded() {
        return requestInterceptor != null;
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.addRequestInterceptor(requestInterceptor);
        LOG.info("Added request interceptor " + requestInterceptor + "");
    }

    public static ProxyAction addRequestInterceptor(RequestInterceptor requestInterceptor) {
        return new RequestInterceptorAction(requestInterceptor);
    }
}
