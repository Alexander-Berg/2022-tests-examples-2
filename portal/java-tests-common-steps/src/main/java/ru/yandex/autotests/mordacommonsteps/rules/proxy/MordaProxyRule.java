package ru.yandex.autotests.mordacommonsteps.rules.proxy;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.openqa.selenium.Proxy;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 07.10.13
 */
public class MordaProxyRule extends TestWatcher {
    private static final Logger LOG = Logger.getLogger(MordaProxyRule.class);
    private final List<ProxyAction> proxyActions;

    private ProxyServer proxyServer;
    private DesiredCapabilities caps;

    public MordaProxyRule(DesiredCapabilities caps) {
        proxyActions = new ArrayList<>();
        this.caps = caps;
    }

    @Override
    protected void starting(Description description) {
        if (!needProxy()) {
            return;
        }
        proxyServer = new ProxyServer(0);
        try {
            proxyServer.start();
//            proxyServer.setCaptureContent(true);
            prepareCapabilities();
        } catch (Exception e) {
            throw new RuntimeException("Failed to start proxy server. " + e.getMessage());
        }
        configure();
    }

    @Override
    protected void finished(Description description) {
        if (!needProxy()) {
            return;
        }
        try {
            LOG.info("Stopping proxy server");
            proxyServer.stop();
        } catch (Exception e) {
            throw new RuntimeException("Failed to stop proxy server. " + e.getMessage());
        }
    }

    public MordaProxyRule addProxyAction(ProxyAction action) {
        proxyActions.add(action);
        return this;
    }

    public MordaProxyRule addProxyActions(Collection<? extends ProxyAction> actions) {
        proxyActions.addAll(actions);
        return this;
    }

    public void configure() {
        for (ProxyAction action : proxyActions) {
            if (action.isNeeded()) {
                action.perform(proxyServer);
            }
        }
    }

    private boolean needProxy() {
        for (ProxyAction action : proxyActions) {
            if (action.isNeeded()) {
                return true;
            }
        }
        return false;
    }

    private void prepareCapabilities() {
        Proxy proxy = null;
        proxy = proxyServer.seleniumProxy();
        if (caps.getBrowserName().contains("chrome")) {
            List<String> switches = (List<String>) caps.getCapability("chrome.switches");
            if (switches == null) {
                switches = new ArrayList<String>();
            }
            switches.add("--proxy-server=" + proxyServer.seleniumProxy().getHttpProxy());
            caps.setCapability("chrome.switches", switches);
        }
        caps.setCapability(CapabilityType.PROXY, proxy);
    }

    public DesiredCapabilities getCapabilities() {
        return caps;
    }

    public ProxyServer getProxyServer() {
        return proxyServer;
    }
}
