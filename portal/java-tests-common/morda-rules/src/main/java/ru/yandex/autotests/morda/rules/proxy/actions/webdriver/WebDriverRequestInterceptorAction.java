package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.RequestInterceptor;
import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.rules.proxy.actions.RequestInterceptorAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public class WebDriverRequestInterceptorAction extends RequestInterceptorAction<MordaBaseWebDriverRule, RequestInterceptor> {

    public static final Logger LOG = Logger.getLogger(WebDriverRequestInterceptorAction.class);
    private ProxyServer proxyServer;

    private WebDriverRequestInterceptorAction(MordaBaseWebDriverRule rule, ProxyServer proxyServer) {
        super(rule);
        this.proxyServer = proxyServer;
    }

    public static WebDriverRequestInterceptorAction webDriverRequestInterceptorAction(MordaBaseWebDriverRule rule, ProxyServer proxyServer){
        return new WebDriverRequestInterceptorAction(rule, proxyServer);
    }

    @Override
    public void perform() {
        if(isNeed){
            proxyServer.addRequestInterceptor(requestInterceptor);
            LOG.info("Added request interceptor " + requestInterceptor + "");
        }
    }
}
